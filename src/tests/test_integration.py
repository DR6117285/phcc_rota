import unittest
from datetime import datetime, timedelta
import pandas as pd

from ..core.staff_manager import StaffManager
from ..core.shift_allocator import ShiftAllocator
from ..core.equity_tracker import EquityTracker
from ..core.audit_logger import AuditLogger
from ..services.excel_report_service import ExcelReportService

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for all integration tests"""
        self.staff_manager = StaffManager()
        self.shift_allocator = ShiftAllocator()
        self.equity_tracker = EquityTracker()
        self.audit_logger = AuditLogger()
        self.report_service = ExcelReportService()

    def test_full_week_allocation(self):
        """Test allocation of all shifts for a full week"""
        # Setup test data
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        # Generate full week schedule
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=start_date,
            end_date=end_date,
            staff=self.staff_manager.get_all_staff()
        )
        
        # Validate schedule
        self.assertIsNotNone(schedule)
        self.assertEqual(len(schedule.get_all_shifts()), 7 * 3)  # 3 shifts per day
        
        # Verify constraints
        for shift in schedule.get_all_shifts():
            self.assertTrue(self.shift_allocator.validate_shift_assignment(shift))
    
    def test_edge_cases(self):
        """Test system behavior with edge cases"""
        # Test with minimum staff
        min_staff = self.staff_manager.get_minimum_staff_required()
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            staff=min_staff
        )
        self.assertIsNotNone(schedule)
        
        # Test with staff on leave
        staff_list = self.staff_manager.get_all_staff()
        staff_list[0].set_leave(datetime.now().date())
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=1),
            staff=staff_list
        )
        self.assertIsNotNone(schedule)
        self.assertNotIn(staff_list[0], schedule.get_assigned_staff())

    def test_performance(self):
        """Test system performance with full staff roster"""
        import time
        
        start_time = time.time()
        
        # Generate a month-long schedule
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=30),
            staff=self.staff_manager.get_all_staff()
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance meets requirements (<5 seconds for a week)
        self.assertLess(execution_time / 4, 5.0)  # Divide by 4 to get approximate week time
        
        # Verify schedule completeness
        self.assertEqual(
            len(schedule.get_all_shifts()),
            30 * 3  # 3 shifts per day for 30 days
        )

    def test_report_generation(self):
        """Test the enhanced report generation system"""
        # Generate some test data
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=7),
            staff=self.staff_manager.get_all_staff()
        )
        
        # Generate enhanced report
        report = self.report_service.generate_detailed_report(schedule)
        
        # Verify report contents
        self.assertIn('shift_distribution', report)
        self.assertIn('team_balance', report)
        self.assertIn('gender_compliance', report)
        self.assertIn('preference_satisfaction', report)

    def test_constraint_validation(self):
        """Test comprehensive constraint validation"""
        start_date = datetime.now().date()
        staff_list = self.staff_manager.get_all_staff()
        
        # Test gender constraints
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=start_date,
            end_date=start_date + timedelta(days=1),
            staff=staff_list
        )
        
        for shift in schedule.get_all_shifts():
            if shift.has_gender_requirement():
                staff = shift.get_assigned_staff()
                self.assertEqual(shift.get_required_gender(), staff.gender)
        
        # Test team balance for TRIAGE shifts
        triage_shifts = [s for s in schedule.get_all_shifts() if s.get_type() == 'TRIAGE']
        teams_assigned = set(s.get_assigned_staff().get_team() for s in triage_shifts)
        self.assertTrue(len(teams_assigned) >= 2, "TRIAGE shifts should be distributed across teams")
        
        # Test consecutive shift constraints
        for staff in staff_list:
            staff_shifts = schedule.get_staff_shifts(staff)
            for i in range(len(staff_shifts) - 1):
                shift1_end = staff_shifts[i].get_end_time()
                shift2_start = staff_shifts[i + 1].get_start_time()
                self.assertGreaterEqual((shift2_start - shift1_end).hours, 8)

    def test_extended_edge_cases(self):
        """Test additional edge cases"""
        start_date = datetime.now().date()
        staff_list = self.staff_manager.get_all_staff()
        
        # Test with multiple staff on leave
        staff_list[0].set_leave(start_date)
        staff_list[1].set_leave(start_date)
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=start_date,
            end_date=start_date + timedelta(days=1),
            staff=staff_list
        )
        self.assertIsNotNone(schedule)
        self.assertNotIn(staff_list[0], schedule.get_assigned_staff())
        self.assertNotIn(staff_list[1], schedule.get_assigned_staff())
        
        # Test with staff preferences
        staff_list[2].set_shift_preference('MORNING', start_date)
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=start_date,
            end_date=start_date + timedelta(days=1),
            staff=staff_list
        )
        staff_shifts = schedule.get_staff_shifts(staff_list[2])
        morning_shifts = [s for s in staff_shifts if s.get_type() == 'MORNING']
        self.assertGreater(len(morning_shifts), 0)
        
        # Test holiday allocation
        holiday_date = start_date + timedelta(days=5)
        schedule = self.shift_allocator.generate_week_schedule(
            start_date=holiday_date,
            end_date=holiday_date + timedelta(days=1),
            staff=staff_list,
            is_holiday=True
        )
        self.assertEqual(len(schedule.get_all_shifts()), 3)  # Still need 3 shifts on holidays
        
    def test_equity_tracking(self):
        """Test equity tracking across multiple allocations"""
        start_date = datetime.now().date()
        staff_list = self.staff_manager.get_all_staff()
        
        # Generate schedules for multiple weeks
        for week in range(4):
            week_start = start_date + timedelta(weeks=week)
            schedule = self.shift_allocator.generate_week_schedule(
                start_date=week_start,
                end_date=week_start + timedelta(days=7),
                staff=staff_list
            )
            
            # Check equity metrics
            equity_metrics = self.equity_tracker.get_metrics()
            self.assertIn('shift_distribution', equity_metrics)
            self.assertIn('weekend_allocation', equity_metrics)
            self.assertIn('night_shift_count', equity_metrics)
            
            # Verify equity balance
            shift_counts = equity_metrics['shift_distribution']
            max_diff = max(shift_counts.values()) - min(shift_counts.values())
            self.assertLess(max_diff, 5)  # No staff member should have >4 more shifts than others

if __name__ == '__main__':
    unittest.main() 