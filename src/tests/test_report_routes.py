import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from src.ui.routes import report_bp
from flask import Flask
from datetime import datetime, timedelta

class TestReportRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(report_bp)
        self.client = self.app.test_client()
        
        # Mock report data
        self.mock_report_data = {
            'shift_distribution': {
                'equity_score': 0.85,
                'staff_shifts': {
                    'staff1': {'total': 10, 'DAY': 6, 'NIGHT': 4}
                }
            },
            'team_balance': {
                'balance_score': 0.9,
                'team_shifts': {
                    'team1': {'total': 20, 'DAY': 12, 'NIGHT': 8}
                }
            },
            'gender_compliance': {
                'compliance_rate': 0.95,
                'violations': []
            },
            'preference_satisfaction': {
                'satisfaction_rate': 0.88,
                'staff_satisfaction': {
                    'staff1': {'total': 10, 'met': 8}
                }
            },
            'conflict_metrics': {
                'conflict_types': {'type1': 5},
                'severity_counts': {'HIGH': 2}
            },
            'visualizations': {
                'shift_distribution': 'base64_encoded_image',
                'team_balance': 'base64_encoded_image',
                'gender_compliance': 'base64_encoded_image',
                'preference_satisfaction': 'base64_encoded_image'
            }
        }
        
        # Mock filter data
        self.mock_teams = [
            {'id': 'team1', 'name': 'Team A'},
            {'id': 'team2', 'name': 'Team B'}
        ]
        self.mock_staff = [
            {'id': 'staff1', 'name': 'John Doe'},
            {'id': 'staff2', 'name': 'Jane Smith'}
        ]

    @patch('src.ui.routes.report_service')
    def test_show_report(self, mock_service):
        """Test the report page route."""
        mock_service.generate_detailed_report.return_value = self.mock_report_data
        
        response = self.client.get('/report')
        
        self.assertEqual(response.status_code, 200)
        mock_service.generate_detailed_report.assert_called_once()
        
        # Check that the response contains expected data
        html_content = response.data.decode()
        self.assertIn('Shift Distribution', html_content)
        self.assertIn('Team Balance', html_content)
        self.assertIn('Gender Compliance', html_content)
        self.assertIn('Preference Satisfaction', html_content)
        self.assertIn('Conflict Metrics', html_content)

    @patch('src.ui.routes.report_service')
    def test_export_report(self, mock_service):
        """Test the report export route."""
        mock_excel = BytesIO(b'mock excel data')
        mock_service.export_to_excel.return_value = mock_excel
        
        response = self.client.get('/report/export')
        
        self.assertEqual(response.status_code, 200)
        mock_service.export_to_excel.assert_called_once()
        self.assertEqual(
            response.headers['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertEqual(
            response.headers['Content-Disposition'],
            'attachment; filename=schedule_report.xlsx'
        )
        self.assertEqual(response.data, b'mock excel data')

    @patch('src.ui.routes.report_service')
    def test_show_report_with_violations(self, mock_service):
        """Test the report page with gender requirement violations."""
        report_data = self.mock_report_data.copy()
        report_data['gender_compliance']['violations'] = [
            {'shift_id': 'shift1', 'required': 'F:2,M:1', 'assigned': 'F:1,M:2'}
        ]
        mock_service.generate_detailed_report.return_value = report_data
        
        response = self.client.get('/report')
        
        self.assertEqual(response.status_code, 200)
        html_content = response.data.decode()
        self.assertIn('Gender Requirement Violations', html_content)
        self.assertIn('shift1', html_content)

    @patch('src.ui.routes.report_service')
    def test_show_report_service_error(self, mock_service):
        """Test error handling when report service fails."""
        mock_service.generate_detailed_report.side_effect = Exception('Service error')
        
        response = self.client.get('/report')
        
        self.assertEqual(response.status_code, 500)

    @patch('src.ui.routes.report_service')
    def test_export_report_service_error(self, mock_service):
        """Test error handling when export service fails."""
        mock_service.export_to_excel.side_effect = Exception('Export error')
        
        response = self.client.get('/report/export')
        
        self.assertEqual(response.status_code, 500)

    @patch('src.ui.routes.report_service')
    def test_show_report_with_filters(self, mock_service):
        """Test the report page with filters."""
        mock_service.generate_detailed_report.return_value = self.mock_report_data
        
        filters = {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'team': 'team1',
            'staff_id': 'staff1',
            'shift_type': 'DAY'
        }
        
        response = self.client.get('/report', query_string=filters)
        
        self.assertEqual(response.status_code, 200)
        mock_service.generate_detailed_report.assert_called_once_with(filters=filters)
        
        html_content = response.data.decode()
        self.assertIn('value="2024-01-01"', html_content)
        self.assertIn('value="2024-01-31"', html_content)
        self.assertIn('value="DAY" selected', html_content)

    @patch('src.ui.routes.report_service')
    def test_export_report_with_filters(self, mock_service):
        """Test the report export with filters."""
        mock_excel = BytesIO(b'mock excel data')
        mock_service.export_to_excel.return_value = mock_excel
        
        filters = {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'team': 'team1',
            'staff_id': 'staff1',
            'shift_type': 'DAY'
        }
        
        response = self.client.get('/report/export', query_string=filters)
        
        self.assertEqual(response.status_code, 200)
        mock_service.export_to_excel.assert_called_once_with(filters=filters)

    @patch('src.ui.routes.report_service')
    def test_get_teams(self, mock_service):
        """Test getting available teams."""
        mock_service.get_available_teams.return_value = self.mock_teams
        
        response = self.client.get('/report/teams')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 'team1')
        self.assertEqual(data[0]['name'], 'Team A')

    @patch('src.ui.routes.report_service')
    def test_get_staff(self, mock_service):
        """Test getting available staff."""
        mock_service.get_available_staff.return_value = self.mock_staff
        
        response = self.client.get('/report/staff')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 'staff1')
        self.assertEqual(data[0]['name'], 'John Doe')

    @patch('src.ui.routes.report_service')
    def test_show_report_error_template(self, mock_service):
        """Test that errors show the error template."""
        mock_service.generate_detailed_report.side_effect = Exception('Service error')
        
        response = self.client.get('/report')
        
        self.assertEqual(response.status_code, 500)
        html_content = response.data.decode()
        self.assertIn('Error', html_content)
        self.assertIn('Failed to generate report', html_content)

    @patch('src.ui.routes.report_service')
    def test_get_teams_error(self, mock_service):
        """Test error handling in teams endpoint."""
        mock_service.get_available_teams.side_effect = Exception('Service error')
        
        response = self.client.get('/report/teams')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)

    @patch('src.ui.routes.report_service')
    def test_get_staff_error(self, mock_service):
        """Test error handling in staff endpoint."""
        mock_service.get_available_staff.side_effect = Exception('Service error')
        
        response = self.client.get('/report/staff')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)

    @patch('src.ui.routes.report_service')
    def test_invalid_date_filter(self, mock_service):
        """Test handling of invalid date filters."""
        filters = {
            'start_date': 'invalid-date',
            'end_date': '2024-01-31'
        }
        
        response = self.client.get('/report', query_string=filters)
        
        self.assertEqual(response.status_code, 500)
        html_content = response.data.decode()
        self.assertIn('Error', html_content)

if __name__ == '__main__':
    unittest.main() 