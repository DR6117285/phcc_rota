import unittest
import time
from datetime import datetime, timedelta
import statistics
import json
import logging
import psutil
import os

from ..core.staff_manager import StaffManager
from ..core.shift_allocator import ShiftAllocator
from ..core.equity_tracker import EquityTracker
from ..services.excel_report_service import ExcelReportService
from ..services.conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)

class PerformanceTests(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for performance testing"""
        self.staff_manager = StaffManager()
        self.shift_allocator = ShiftAllocator()
        self.conflict_resolver = ConflictResolver()
        self.equity_tracker = EquityTracker()
        self.report_service = ExcelReportService()
        self.process = psutil.Process(os.getpid())
        self.results = {}

    def tearDown(self):
        """Save benchmark results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"benchmark_results_{timestamp}.json", "w") as f:
            json.dump(self.results, f, indent=2)

    def _measure_execution_time(self, func, iterations=5):
        """Measure execution time with multiple iterations"""
        times = []
        for _ in range(iterations):
            start_time = time.time()
            result = func()
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            'min': min(times),
            'max': max(times),
            'avg': statistics.mean(times),
            'median': statistics.median(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }

    def _measure_memory_usage(self, func):
        """Helper to measure memory usage of a function"""
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        result = func()
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        return final_memory - initial_memory, result

    def test_week_allocation_performance(self):
        """Test performance of week-long schedule generation"""
        def generate_week():
            return self.shift_allocator.generate_week_schedule(
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=7),
                staff=self.staff_manager.get_all_staff()
            )
        
        execution_time, schedule = self._measure_execution_time(generate_week)
        memory_usage, _ = self._measure_memory_usage(generate_week)
        
        # Verify performance requirements
        self.assertLess(execution_time, 5.0)  # Should take less than 5 seconds
        self.assertLess(memory_usage, 100)  # Should use less than 100MB additional memory
        
        # Verify schedule completeness
        self.assertEqual(len(schedule.get_all_shifts()), 7 * 3)  # 3 shifts per day

    def test_conflict_resolution_performance(self):
        """Test performance of conflict detection and resolution"""
        # Generate a schedule with known conflicts
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=7),
            staff=self.staff_manager.get_all_staff()
        )
        
        # Test conflict detection performance
        def detect_conflicts():
            return self.conflict_resolver.detect_conflicts(schedule)
        
        detection_time, conflicts = self._measure_execution_time(detect_conflicts)
        self.assertLess(detection_time, 1.0)  # Should take less than 1 second
        
        # Test resolution performance
        if conflicts:
            def resolve_conflicts():
                for conflict in conflicts:
                    resolutions = self.conflict_resolver.suggest_resolutions(conflict)
                    if resolutions:
                        self.conflict_resolver.apply_resolution(conflict, resolutions[0])
            
            resolution_time, _ = self._measure_execution_time(resolve_conflicts)
            self.assertLess(resolution_time, 2.0)  # Should take less than 2 seconds

    def test_report_generation_performance(self):
        """Test performance of report generation"""
        # Generate test data
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=7),
            staff=self.staff_manager.get_all_staff()
        )
        
        def generate_report():
            return self.report_service.generate_detailed_report(schedule)
        
        execution_time, report = self._measure_execution_time(generate_report)
        memory_usage, _ = self._measure_memory_usage(generate_report)
        
        # Verify performance
        self.assertLess(execution_time, 3.0)  # Should take less than 3 seconds
        self.assertLess(memory_usage, 50)  # Should use less than 50MB additional memory

    def test_large_scale_performance(self):
        """Test system performance with large datasets"""
        # Generate a month-long schedule
        def generate_month():
            return self.shift_allocator.generate_week_schedule(
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=30),
                staff=self.staff_manager.get_all_staff()
            )
        
        execution_time, schedule = self._measure_execution_time(generate_month)
        memory_usage, _ = self._measure_memory_usage(generate_month)
        
        # Scale requirements to month length (4 weeks)
        self.assertLess(execution_time, 20.0)  # Should take less than 20 seconds
        self.assertLess(memory_usage, 200)  # Should use less than 200MB additional memory
        
        # Test conflict resolution on large schedule
        def process_conflicts():
            conflicts = self.conflict_resolver.detect_conflicts(schedule)
            for conflict in conflicts[:10]:  # Process first 10 conflicts
                resolutions = self.conflict_resolver.suggest_resolutions(conflict)
                if resolutions:
                    self.conflict_resolver.apply_resolution(conflict, resolutions[0])
        
        conflict_time, _ = self._measure_execution_time(process_conflicts)
        self.assertLess(conflict_time, 5.0)  # Should take less than 5 seconds

    def test_concurrent_operations(self):
        """Test performance under concurrent operations"""
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        def concurrent_task():
            schedule = self.shift_allocator.generate_week_schedule(
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=7),
                staff=self.staff_manager.get_all_staff()
            )
            conflicts = self.conflict_resolver.detect_conflicts(schedule)
            if conflicts:
                resolutions = self.conflict_resolver.suggest_resolutions(conflicts[0])
                if resolutions:
                    self.conflict_resolver.apply_resolution(conflicts[0], resolutions[0])
            return schedule
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(concurrent_task) for _ in range(3)]
            schedules = [f.result() for f in futures]
        end_time = time.time()
        
        total_time = end_time - start_time
        self.assertLess(total_time, 15.0)  # Should handle 3 concurrent operations in less than 15 seconds
        self.assertEqual(len(schedules), 3)

if __name__ == '__main__':
    unittest.main() 