import unittest
from datetime import datetime, date, timedelta
from ..services.conflict_resolver import ConflictResolver
from ..interfaces.conflict_interfaces import ConflictType, ConflictSeverity, ConflictResolution

class TestConflictResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = ConflictResolver()
        self.test_schedule = self._create_test_schedule()
        
    def _create_test_schedule(self):
        """Create a test schedule with known conflicts"""
        return {
            'shifts': [
                # Gender requirement conflict
                {
                    'id': 'shift1',
                    'type': 'DAY',
                    'start_time': '2024-03-20T09:00:00',
                    'end_time': '2024-03-20T17:00:00',
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
                    'start_time': '2024-03-20T23:00:00',
                    'end_time': '2024-03-21T07:00:00',
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
                    'start_time': '2024-03-21T07:00:00',
                    'end_time': '2024-03-21T15:00:00',
                    'gender_requirement': None,
                    'assigned_staff': {
                        'id': 'staff2',
                        'gender': 'F',
                        'team': 'B'
                    }
                },
                # Staff unavailable conflict
                {
                    'id': 'shift4',
                    'type': 'DAY',
                    'start_time': '2024-03-22T09:00:00',
                    'end_time': '2024-03-22T17:00:00',
                    'gender_requirement': None,
                    'assigned_staff': {
                        'id': 'staff3',
                        'gender': 'M',
                        'team': 'A',
                        'leave_dates': ['2024-03-22']
                    }
                }
            ]
        }
    
    def test_detect_gender_requirement_conflict(self):
        """Test detection of gender requirement conflicts"""
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        gender_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.GENDER_REQUIREMENT]
        
        self.assertEqual(len(gender_conflicts), 1)
        conflict = gender_conflicts[0]
        self.assertEqual(conflict.severity, ConflictSeverity.CRITICAL)
        self.assertEqual(conflict.affected_shifts[0]['id'], 'shift1')
        self.assertEqual(conflict.affected_staff[0], 'staff1')
    
    def test_detect_consecutive_shifts_conflict(self):
        """Test detection of consecutive shifts conflicts"""
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        consecutive_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.CONSECUTIVE_SHIFTS]
        
        self.assertEqual(len(consecutive_conflicts), 1)
        conflict = consecutive_conflicts[0]
        self.assertEqual(conflict.severity, ConflictSeverity.HIGH)
        self.assertEqual(len(conflict.affected_shifts), 2)
        self.assertEqual(conflict.affected_staff[0], 'staff2')
    
    def test_detect_staff_unavailable_conflict(self):
        """Test detection of staff unavailability conflicts"""
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        unavailable_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.STAFF_UNAVAILABLE]
        
        self.assertEqual(len(unavailable_conflicts), 1)
        conflict = unavailable_conflicts[0]
        self.assertEqual(conflict.severity, ConflictSeverity.CRITICAL)
        self.assertEqual(conflict.affected_shifts[0]['id'], 'shift4')
        self.assertEqual(conflict.affected_staff[0], 'staff3')
    
    def test_analyze_conflict(self):
        """Test conflict analysis functionality"""
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        analysis = self.resolver.analyze_conflict(conflicts[0])
        
        self.assertIn('type', analysis)
        self.assertIn('severity', analysis)
        self.assertIn('description', analysis)
        self.assertIn('affected_shifts', analysis)
        self.assertIn('affected_staff', analysis)
        self.assertIn('metrics', analysis)
    
    def test_suggest_resolutions(self):
        """Test resolution suggestion functionality"""
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        gender_conflict = [c for c in conflicts if c.conflict_type == ConflictType.GENDER_REQUIREMENT][0]
        resolutions = self.resolver.suggest_resolutions(gender_conflict)
        
        self.assertTrue(len(resolutions) > 0)
        resolution = resolutions[0]
        self.assertIn('type', resolution)
        self.assertIn('description', resolution)
        self.assertIn('details', resolution)
    
    def test_get_distribution_metrics(self):
        """Test distribution metrics calculation"""
        start_date = date(2024, 3, 20)
        end_date = date(2024, 3, 22)
        metrics = self.resolver.get_distribution_metrics(
            self.test_schedule, start_date, end_date
        )
        
        self.assertIn('shift_counts', metrics)
        self.assertIn('team_distribution', metrics)
        self.assertIn('gender_distribution', metrics)
        self.assertIn('workload_metrics', metrics)
        self.assertIn('preference_satisfaction', metrics)
    
    def test_validate_manual_resolution(self):
        """Test validation of manual resolutions"""
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        gender_conflict = [c for c in conflicts if c.conflict_type == ConflictType.GENDER_REQUIREMENT][0]
        
        # Test invalid changes
        invalid_changes = {
            'new_assignments': {'shift1': 'staff4'}  # Missing affected_shifts
        }
        errors = self.resolver.validate_manual_resolution(gender_conflict, invalid_changes)
        self.assertTrue(len(errors) > 0)
        
        # Test valid changes
        valid_changes = {
            'affected_shifts': ['shift1'],
            'new_assignments': {'shift1': 'staff4'}
        }
        errors = self.resolver.validate_manual_resolution(gender_conflict, valid_changes)
        self.assertEqual(len(errors), 0)
    
    def test_get_staff_impact(self):
        """Test staff impact analysis"""
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        gender_conflict = [c for c in conflicts if c.conflict_type == ConflictType.GENDER_REQUIREMENT][0]
        resolution = {
            'type': ConflictResolution.SWAP_STAFF.value,
            'details': {
                'shift_id': 'shift1',
                'new_staff_id': 'staff4'
            }
        }
        
        impact = self.resolver.get_staff_impact(gender_conflict, resolution)
        self.assertIn('directly_affected', impact)
        self.assertIn('indirectly_affected', impact)
        self.assertIn('workload_changes', impact)
        self.assertIn('preference_impact', impact)
    
    def test_resolution_history(self):
        """Test resolution history tracking"""
        # Initially empty
        history = self.resolver.get_resolution_history(self.test_schedule)
        self.assertEqual(len(history), 0)
        
        # Apply a resolution
        conflicts = self.resolver.detect_conflicts(self.test_schedule)
        gender_conflict = [c for c in conflicts if c.conflict_type == ConflictType.GENDER_REQUIREMENT][0]
        resolution = {
            'type': ConflictResolution.SWAP_STAFF.value,
            'description': 'Swap with eligible staff member',
            'details': {
                'shift_id': 'shift1',
                'new_staff_id': 'staff4'
            }
        }
        
        self.resolver.apply_resolution(gender_conflict, resolution)
        
        # Check history
        history = self.resolver.get_resolution_history(self.test_schedule)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['conflict_type'], ConflictType.GENDER_REQUIREMENT.value)
        self.assertEqual(history[0]['resolution_type'], ConflictResolution.SWAP_STAFF.value)

if __name__ == '__main__':
    unittest.main() 