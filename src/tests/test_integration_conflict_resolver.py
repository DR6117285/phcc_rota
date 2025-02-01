import unittest
from datetime import datetime, timedelta
import pandas as pd

from ..core.staff_manager import StaffManager
from ..core.shift_allocator import ShiftAllocator
from ..services.conflict_resolver import ConflictResolver
from ..core.equity_tracker import EquityTracker
from ..core.audit_logger import AuditLogger

class ConflictResolverIntegrationTests(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures for conflict resolver integration tests"""
        self.staff_manager = StaffManager()
        self.shift_allocator = ShiftAllocator()
        self.conflict_resolver = ConflictResolver()
        self.equity_tracker = EquityTracker()
        self.audit_logger = AuditLogger()
        
        # Create test schedule with known conflicts
        self.test_schedule = self._create_test_schedule()
    
    def _create_test_schedule(self):
        """Create a test schedule with various types of conflicts"""
        start_date = datetime.now().date()
        staff_list = self.staff_manager.get_all_staff()
        
        # Create a schedule with intentional conflicts
        schedule = {
            'shifts': [
                # Gender requirement conflict
                {
                    'id': 'shift1',
                    'type': 'DAY',
                    'start_time': start_date.isoformat(),
                    'end_time': (start_date + timedelta(hours=8)).isoformat(),
                    'gender_requirement': 'F',
                    'assigned_staff': {
                        'id': 'staff1',
                        'gender': 'M',
                        'team': 'A'
                    }
                },
                # Consecutive shifts conflict
                {
                    'id': 'shift2',
                    'type': 'NIGHT',
                    'start_time': (start_date + timedelta(hours=23)).isoformat(),
                    'end_time': (start_date + timedelta(days=1, hours=7)).isoformat(),
                    'gender_requirement': None,
                    'assigned_staff': {
                        'id': 'staff2',
                        'gender': 'F',
                        'team': 'B'
                    }
                },
                {
                    'id': 'shift3',
                    'type': 'DAY',
                    'start_time': (start_date + timedelta(days=1, hours=7)).isoformat(),
                    'end_time': (start_date + timedelta(days=1, hours=15)).isoformat(),
                    'gender_requirement': None,
                    'assigned_staff': {
                        'id': 'staff2',
                        'gender': 'F',
                        'team': 'B'
                    }
                }
            ]
        }
        return schedule

    def test_conflict_detection_and_resolution(self):
        """Test end-to-end conflict detection and resolution"""
        # Detect conflicts
        conflicts = self.conflict_resolver.detect_conflicts(self.test_schedule)
        self.assertTrue(len(conflicts) >= 2)  # Should find at least gender and consecutive conflicts
        
        # Verify conflict types
        conflict_types = [c.conflict_type for c in conflicts]
        self.assertIn('GENDER_REQUIREMENT', [ct.value for ct in conflict_types])
        self.assertIn('CONSECUTIVE_SHIFTS', [ct.value for ct in conflict_types])
        
        # Test resolution suggestions
        for conflict in conflicts:
            resolutions = self.conflict_resolver.suggest_resolutions(conflict)
            self.assertTrue(len(resolutions) > 0)
            
            # Apply first suggested resolution
            success = self.conflict_resolver.apply_resolution(conflict, resolutions[0])
            self.assertTrue(success)
        
        # Verify conflicts are resolved
        remaining_conflicts = self.conflict_resolver.detect_conflicts(self.test_schedule)
        self.assertEqual(len(remaining_conflicts), 0)

    def test_schedule_modification_integrity(self):
        """Test that schedule modifications maintain data integrity"""
        original_shift_count = len(self.test_schedule['shifts'])
        
        # Apply various modifications
        conflicts = self.conflict_resolver.detect_conflicts(self.test_schedule)
        for conflict in conflicts:
            resolutions = self.conflict_resolver.suggest_resolutions(conflict)
            if resolutions:
                self.conflict_resolver.apply_resolution(conflict, resolutions[0])
        
        # Verify schedule integrity
        self.assertEqual(len(self.test_schedule['shifts']), original_shift_count)
        for shift in self.test_schedule['shifts']:
            self.assertIn('id', shift)
            self.assertIn('type', shift)
            self.assertIn('start_time', shift)
            self.assertIn('end_time', shift)
            self.assertIn('assigned_staff', shift)

    def test_resolution_history_tracking(self):
        """Test that resolution history is properly tracked"""
        # Apply some resolutions
        conflicts = self.conflict_resolver.detect_conflicts(self.test_schedule)
        applied_resolutions = []
        
        for conflict in conflicts:
            resolutions = self.conflict_resolver.suggest_resolutions(conflict)
            if resolutions:
                success = self.conflict_resolver.apply_resolution(conflict, resolutions[0])
                if success:
                    applied_resolutions.append((conflict, resolutions[0]))
        
        # Check resolution history
        history = self.conflict_resolver.get_resolution_history(self.test_schedule)
        self.assertEqual(len(history), len(applied_resolutions))
        
        for entry in history:
            self.assertIn('timestamp', entry)
            self.assertIn('conflict_type', entry)
            self.assertIn('resolution_type', entry)
            self.assertIn('affected_shifts', entry)
            self.assertIn('affected_staff', entry)

    def test_manual_resolution_validation(self):
        """Test validation of manual conflict resolutions"""
        conflicts = self.conflict_resolver.detect_conflicts(self.test_schedule)
        self.assertTrue(len(conflicts) > 0)
        
        conflict = conflicts[0]
        
        # Test invalid manual resolution
        invalid_changes = {
            'new_assignments': {'shift1': 'staff4'}  # Missing affected_shifts
        }
        errors = self.conflict_resolver.validate_manual_resolution(conflict, invalid_changes)
        self.assertTrue(len(errors) > 0)
        
        # Test valid manual resolution
        valid_changes = {
            'affected_shifts': ['shift1'],
            'new_assignments': {'shift1': 'staff4'}
        }
        errors = self.conflict_resolver.validate_manual_resolution(conflict, valid_changes)
        self.assertEqual(len(errors), 0)

    def test_staff_impact_analysis(self):
        """Test analysis of resolution impact on staff"""
        conflicts = self.conflict_resolver.detect_conflicts(self.test_schedule)
        self.assertTrue(len(conflicts) > 0)
        
        for conflict in conflicts:
            resolutions = self.conflict_resolver.suggest_resolutions(conflict)
            if resolutions:
                impact = self.conflict_resolver.get_staff_impact(conflict, resolutions[0])
                
                self.assertIn('directly_affected', impact)
                self.assertIn('indirectly_affected', impact)
                self.assertIn('workload_changes', impact)
                self.assertIn('preference_impact', impact)

if __name__ == '__main__':
    unittest.main() 