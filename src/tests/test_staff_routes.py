import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from src.ui.staff_routes import staff_bp
from src.services.staff_management_service import SkillLevel
import json

class TestStaffRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.register_blueprint(staff_bp)
        self.client = self.app.test_client()
        
        # Mock staff data
        self.test_staff = {
            'id': 'staff1',
            'name': 'John Doe',
            'gender': 'M',
            'role': 'Doctor',
            'team': 'TeamA',
            'skills': {'Surgery': SkillLevel.SENIOR},
            'certifications': {'Advanced Life Support'},
            'contact': {
                'email': 'john@hospital.com',
                'phone': '1234567890'
            }
        }
    
    @patch('src.ui.staff_routes.staff_service')
    def test_staff_list(self, mock_service):
        """Test staff list page."""
        mock_service.staff_profiles = {'staff1': self.test_staff}
        mock_service.teams = {'TeamA': {'staff1'}}
        mock_service.skills_registry = {'Surgery'}
        mock_service.certifications_registry = {'Advanced Life Support'}
        
        response = self.client.get('/staff')
        
        self.assertEqual(response.status_code, 200)
        html_content = response.data.decode()
        self.assertIn('John Doe', html_content)
        self.assertIn('TeamA', html_content)
        self.assertIn('Surgery', html_content)
    
    @patch('src.ui.staff_routes.staff_service')
    def test_add_staff(self, mock_service):
        """Test adding a new staff member."""
        mock_service.add_staff_member.return_value = 'staff1'
        
        staff_data = {
            'name': 'John Doe',
            'gender': 'M',
            'role': 'Doctor'
        }
        
        response = self.client.post('/staff',
                                  data=json.dumps(staff_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 'staff1')
        mock_service.add_staff_member.assert_called_once_with(staff_data)
    
    @patch('src.ui.staff_routes.staff_service')
    def test_get_staff(self, mock_service):
        """Test getting staff member details."""
        mock_service.get_staff_member.return_value = self.test_staff
        
        response = self.client.get('/staff/staff1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['role'], 'Doctor')
        mock_service.get_staff_member.assert_called_once_with('staff1')
    
    @patch('src.ui.staff_routes.staff_service')
    def test_update_staff(self, mock_service):
        """Test updating staff member details."""
        mock_service.update_staff_member.return_value = self.test_staff
        
        updates = {
            'name': 'John Smith',
            'email': 'john.smith@hospital.com'
        }
        
        response = self.client.put('/staff/staff1',
                                 data=json.dumps(updates),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        mock_service.update_staff_member.assert_called_once_with('staff1', updates)
    
    @patch('src.ui.staff_routes.staff_service')
    def test_add_skill(self, mock_service):
        """Test adding a skill to staff member."""
        skill_data = {
            'skill_name': 'Surgery',
            'level': 'SENIOR'
        }
        
        response = self.client.post('/staff/staff1/skills',
                                  data=json.dumps(skill_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        mock_service.add_skill.assert_called_once_with(
            'staff1',
            'Surgery',
            SkillLevel.SENIOR
        )
    
    @patch('src.ui.staff_routes.staff_service')
    def test_add_certification(self, mock_service):
        """Test adding a certification to staff member."""
        cert_data = {
            'certification': 'Advanced Life Support'
        }
        
        response = self.client.post('/staff/staff1/certifications',
                                  data=json.dumps(cert_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        mock_service.add_certification.assert_called_once_with(
            'staff1',
            'Advanced Life Support',
            None
        )
    
    @patch('src.ui.staff_routes.staff_service')
    def test_update_availability(self, mock_service):
        """Test updating staff availability."""
        availability_data = {
            'availability_type': 'regular',
            'dates': ['2024-01-01', '2024-01-02'],
            'is_available': True
        }
        
        response = self.client.post('/staff/staff1/availability',
                                  data=json.dumps(availability_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        mock_service.update_availability.assert_called_once()
    
    @patch('src.ui.staff_routes.staff_service')
    def test_update_preferences(self, mock_service):
        """Test updating staff preferences."""
        preference_data = {
            'preference_type': 'shift_types',
            'preferences': ['DAY', 'EVENING']
        }
        
        response = self.client.post('/staff/staff1/preferences',
                                  data=json.dumps(preference_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        mock_service.update_preferences.assert_called_once_with(
            'staff1',
            'shift_types',
            {'DAY', 'EVENING'}
        )
    
    @patch('src.ui.staff_routes.staff_service')
    def test_get_available_staff(self, mock_service):
        """Test getting available staff."""
        mock_service.get_available_staff.return_value = [self.test_staff]
        
        response = self.client.get('/staff/available?date=2024-01-01&shift_type=DAY')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'John Doe')
    
    @patch('src.ui.staff_routes.staff_service')
    def test_get_staff_with_skill(self, mock_service):
        """Test getting staff with specific skill."""
        mock_service.get_staff_with_skill.return_value = [self.test_staff]
        
        response = self.client.get('/staff/skills/Surgery?min_level=JUNIOR')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'John Doe')
    
    @patch('src.ui.staff_routes.staff_service')
    def test_get_staff_with_certification(self, mock_service):
        """Test getting staff with specific certification."""
        mock_service.get_staff_with_certification.return_value = [self.test_staff]
        
        response = self.client.get('/staff/certifications/Advanced Life Support')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'John Doe')
    
    @patch('src.ui.staff_routes.staff_service')
    def test_staff_list_error(self, mock_service):
        """Test error handling in staff list."""
        mock_service.staff_profiles = MagicMock(side_effect=Exception('Database error'))
        
        response = self.client.get('/staff')
        
        self.assertEqual(response.status_code, 500)
        html_content = response.data.decode()
        self.assertIn('Failed to load staff management page', html_content)
    
    @patch('src.ui.staff_routes.staff_service')
    def test_add_staff_validation_error(self, mock_service):
        """Test validation error when adding staff."""
        mock_service.add_staff_member.side_effect = ValueError('Missing required field')
        
        staff_data = {'name': 'John Doe'}  # Missing required fields
        
        response = self.client.post('/staff',
                                  data=json.dumps(staff_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Missing required field', data['error'])

if __name__ == '__main__':
    unittest.main() 