import unittest
import time
import psutil
import os
from datetime import datetime, date, timedelta
from ..services.conflict_resolver import ConflictResolver

class TestConflictResolverPerformance(unittest.TestCase):
    def setUp(self):
        self.resolver = ConflictResolver()
        self.process = psutil.Process(os.getpid())
    
    def _create_large_schedule(self, num_shifts):
        """Create a test schedule with specified number of shifts"""
        shifts = []
        staff_per_team = 20
        teams = ['A', 'B', 'C']
        
        start_date = datetime(2024, 3, 1)
        shift_types = ['DAY', 'NIGHT', 'EVENING']
        
        for i in range(num_shifts):
            shift_date = start_date + timedelta(hours=8 * (i // 3))
            shift_type = shift_types[i % 3]
            team = teams[i % 3]
            staff_id = f'staff{i % (staff_per_team * 3)}'
            
            shifts.append({
                'id': f'shift{i}',
                'type': shift_type,
                'start_time': shift_date.isoformat(),
                'end_time': (shift_date + timedelta(hours=8)).isoformat(),
                'gender_requirement': 'F' if i % 5 == 0 else None,
                'assigned_staff': {
                    'id': staff_id,
                    'gender': 'F' if i % 2 == 0 else 'M',
                    'team': team,
                    'leave_dates': [
                        (start_date + timedelta(days=i % 7)).date().isoformat()
                    ] if i % 10 == 0 else []
                }
            })
        
        return {'shifts': shifts}
    
    def _measure_memory_usage(self):
        """Measure current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def test_conflict_detection_performance(self):
        """Test performance of conflict detection with different schedule sizes"""
        schedule_sizes = [100, 500, 1000]  # Number of shifts
        max_detection_time = 2.0  # Maximum acceptable time in seconds
        
        results = []
        for size in schedule_sizes:
            schedule = self._create_large_schedule(size)
            
            # Measure time
            start_time = time.time()
            conflicts = self.resolver.detect_conflicts(schedule)
            end_time = time.time()
            
            detection_time = end_time - start_time
            results.append({
                'size': size,
                'time': detection_time,
                'conflicts_found': len(conflicts)
            })
            
            # Assert performance requirements
            self.assertLess(
                detection_time, 
                max_detection_time,
                f"Conflict detection for {size} shifts took {detection_time:.2f}s"
            )
    
    def test_memory_usage(self):
        """Test memory usage during conflict detection"""
        large_schedule = self._create_large_schedule(1000)
        max_memory_increase = 100  # Maximum acceptable memory increase in MB
        
        # Measure baseline memory
        baseline_memory = self._measure_memory_usage()
        
        # Perform conflict detection
        conflicts = self.resolver.detect_conflicts(large_schedule)
        
        # Measure memory after operation
        peak_memory = self._measure_memory_usage()
        memory_increase = peak_memory - baseline_memory
        
        self.assertLess(
            memory_increase,
            max_memory_increase,
            f"Memory usage increased by {memory_increase:.2f}MB"
        )
    
    def test_resolution_suggestion_performance(self):
        """Test performance of resolution suggestions"""
        schedule = self._create_large_schedule(500)
        max_suggestion_time = 1.0  # Maximum acceptable time in seconds
        
        # Get conflicts first
        conflicts = self.resolver.detect_conflicts(schedule)
        self.assertTrue(len(conflicts) > 0, "No conflicts found for testing")
        
        # Measure suggestion time
        start_time = time.time()
        resolutions = self.resolver.suggest_resolutions(conflicts[0])
        end_time = time.time()
        
        suggestion_time = end_time - start_time
        self.assertLess(
            suggestion_time,
            max_suggestion_time,
            f"Resolution suggestion took {suggestion_time:.2f}s"
        )
    
    def test_distribution_metrics_performance(self):
        """Test performance of distribution metrics calculation"""
        schedule = self._create_large_schedule(1000)
        max_calculation_time = 1.0  # Maximum acceptable time in seconds
        
        start_date = date(2024, 3, 1)
        end_date = date(2024, 3, 31)
        
        # Measure calculation time
        start_time = time.time()
        metrics = self.resolver.get_distribution_metrics(
            schedule, start_date, end_date
        )
        end_time = time.time()
        
        calculation_time = end_time - start_time
        self.assertLess(
            calculation_time,
            max_calculation_time,
            f"Metrics calculation took {calculation_time:.2f}s"
        )
    
    def test_scalability(self):
        """Test how performance scales with schedule size"""
        sizes = [100, 200, 400, 800]
        times = []
        
        for size in sizes:
            schedule = self._create_large_schedule(size)
            
            start_time = time.time()
            conflicts = self.resolver.detect_conflicts(schedule)
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        # Check if time increases roughly linearly
        # Compare ratios of time increase vs size increase
        for i in range(1, len(sizes)):
            size_ratio = sizes[i] / sizes[i-1]
            time_ratio = times[i] / times[i-1]
            
            # Time should increase less than quadratically
            self.assertLess(
                time_ratio,
                size_ratio * size_ratio,
                f"Performance scaling is worse than quadratic at size {sizes[i]}"
            )

if __name__ == '__main__':
    unittest.main() 