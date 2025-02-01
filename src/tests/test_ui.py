import unittest
from datetime import datetime, timedelta
import json
from flask import template_rendered
from contextlib import contextmanager
from ..ui.conflict_resolution_ui import ConflictResolutionUI
from ..services.conflict_resolver import ConflictResolver
from ..core.staff_manager import StaffManager
from ..core.shift_allocator import ShiftAllocator

class TestConflictResolutionUI(unittest.TestCase):
    @contextmanager
    def captured_templates(self):
        """Helper to capture templates being rendered"""
        recorded = []
        def record(sender, template, context, **extra):
            recorded.append((template, context))
        template_rendered.connect(record)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record)

    def setUp(self):
        """Set up test client and mocked data"""
        self.ui = ConflictResolutionUI()
        self.client = self.ui.app.test_client()
        self.app_context = self.ui.app.app_context()
        self.app_context.push()
        
        # Create test schedule with known conflicts
        self.test_schedule = self._create_test_schedule()
        
        # Mock the get_current_schedule method
        def mock_get_schedule():
            return self.test_schedule
        self.ui._get_current_schedule = mock_get_schedule
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def _create_test_schedule(self):
        """Create a test schedule with known conflicts"""
        start_date = datetime.now().date()
        return {
            'shifts': [
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
                }
            ]
        }

    def test_list_conflicts_route(self):
        """Test the conflicts listing route"""
        with self.captured_templates() as templates:
            response = self.client.get('/conflicts')
            self.assertEqual(response.status_code, 200)
            
            # Verify template and context
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'conflicts.html')
            self.assertIn('conflicts', context)
            self.assertIn('schedule', context)
            
            # Verify conflicts are detected
            conflicts = context['conflicts']
            self.assertTrue(len(conflicts) > 0)
            
            # Verify conflict data structure
            conflict = conflicts[0]
            self.assertIn('id', conflict)
            self.assertIn('severity', conflict)
            self.assertIn('description', conflict)
            self.assertIn('conflict_type', conflict)
            self.assertIn('affected_shifts', conflict)
            self.assertIn('affected_staff', conflict)

    def test_conflict_details_route(self):
        """Test the conflict details route"""
        # First get a conflict ID from the list
        response = self.client.get('/conflicts')
        conflicts_data = self.ui.conflict_resolver.detect_conflicts(self.test_schedule)
        conflict_id = conflicts_data[0].id
        
        # Test details page
        with self.captured_templates() as templates:
            response = self.client.get(f'/conflicts/{conflict_id}/details')
            self.assertEqual(response.status_code, 200)
            
            # Verify template and context
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'conflict_details.html')
            self.assertIn('conflict', context)
            self.assertIn('analysis', context)
            self.assertIn('resolutions', context)
            
            # Verify analysis data
            analysis = context['analysis']
            self.assertIn('type', analysis)
            self.assertIn('severity', analysis)
            self.assertIn('impact_analysis', analysis)
            
            # Verify resolutions
            resolutions = context['resolutions']
            self.assertTrue(len(resolutions) > 0)
            resolution = resolutions[0]
            self.assertIn('description', resolution)
            self.assertIn('type', resolution)

    def test_resolve_conflict_route(self):
        """Test the conflict resolution route"""
        # Get a conflict and its resolution
        conflicts_data = self.ui.conflict_resolver.detect_conflicts(self.test_schedule)
        conflict = conflicts_data[0]
        resolutions = self.ui.conflict_resolver.suggest_resolutions(conflict)
        
        # Test resolution application
        response = self.client.post(
            f'/conflicts/{conflict.id}/resolve',
            json={
                'resolution_index': 0,
                'resolution': resolutions[0]
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        
        # Verify conflict is resolved
        remaining_conflicts = self.ui.conflict_resolver.detect_conflicts(self.test_schedule)
        self.assertTrue(
            len(remaining_conflicts) < len(conflicts_data),
            "Conflict should be resolved"
        )

    def test_impact_analysis_route(self):
        """Test the impact analysis route"""
        # Get a conflict and resolution
        conflicts_data = self.ui.conflict_resolver.detect_conflicts(self.test_schedule)
        conflict = conflicts_data[0]
        resolutions = self.ui.conflict_resolver.suggest_resolutions(conflict)
        
        # Test impact analysis
        response = self.client.post(
            '/conflicts/impact-analysis',
            json={
                'conflict_id': conflict.id,
                'resolution': resolutions[0]
            }
        )
        self.assertEqual(response.status_code, 200)
        impact = json.loads(response.data)
        
        # Verify impact data structure
        self.assertIn('directly_affected', impact)
        self.assertIn('indirectly_affected', impact)
        self.assertIn('workload_changes', impact)
        self.assertIn('preference_impact', impact)

    def test_resolution_history_route(self):
        """Test the resolution history route"""
        with self.captured_templates() as templates:
            response = self.client.get('/conflicts/history')
            self.assertEqual(response.status_code, 200)
            
            # Verify template and context
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'resolution_history.html')
            self.assertIn('history', context)
            
            # Verify history entries
            history = context['history']
            self.assertIsInstance(history, list)
            
            # If there are entries, verify their structure
            if history:
                entry = history[0]
                self.assertIn('timestamp', entry)
                self.assertIn('conflict_type', entry)
                self.assertIn('resolution_type', entry)
                self.assertIn('affected_shifts', entry)
                self.assertIn('affected_staff', entry)

    def test_error_handling(self):
        """Test error handling in routes"""
        # Test invalid conflict ID
        response = self.client.get('/conflicts/invalid-id/details')
        self.assertEqual(response.status_code, 404)
        
        # Test invalid resolution data
        response = self.client.post(
            '/conflicts/some-id/resolve',
            json={}
        )
        self.assertEqual(response.status_code, 400)
        
        # Test invalid impact analysis request
        response = self.client.post(
            '/conflicts/impact-analysis',
            json={}
        )
        self.assertEqual(response.status_code, 400)

    def test_filter_functionality(self):
        """Test history filtering functionality"""
        # Add some test history entries
        conflicts_data = self.ui.conflict_resolver.detect_conflicts(self.test_schedule)
        conflict = conflicts_data[0]
        resolutions = self.ui.conflict_resolver.suggest_resolutions(conflict)
        self.ui.conflict_resolver.apply_resolution(conflict, resolutions[0])
        
        # Test date filter
        response = self.client.get('/conflicts/history?startDate=2024-01-01&endDate=2024-12-31')
        self.assertEqual(response.status_code, 200)
        
        # Test conflict type filter
        response = self.client.get('/conflicts/history?conflictType=GENDER_REQUIREMENT')
        self.assertEqual(response.status_code, 200)
        
        # Test resolution type filter
        response = self.client.get('/conflicts/history?resolutionType=SWAP_STAFF')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 