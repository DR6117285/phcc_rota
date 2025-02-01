import unittest
from datetime import datetime, timedelta
from ..services.staff_management_service import StaffManagementService, SkillLevel

class TestStaffManagementService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.service = StaffManagementService()
        self.test_staff_data = {
            'name': 'John Doe',
            'gender': 'M',
            'role': 'Doctor',
            'email': 'john@hospital.com',
            'phone': '1234567890',
            'team': 'TeamA'
        }
    
    def test_add_staff_member(self):
        """Test adding a new staff member."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        self.assertIsNotNone(staff_id)
        profile = self.service.get_staff_member(staff_id)
        
        self.assertEqual(profile['name'], 'John Doe')
        self.assertEqual(profile['gender'], 'M')
        self.assertEqual(profile['role'], 'Doctor')
        self.assertEqual(profile['team'], 'TeamA')
        self.assertEqual(profile['contact']['email'], 'john@hospital.com')
        self.assertEqual(profile['contact']['phone'], '1234567890')
    
    def test_add_staff_member_missing_required_field(self):
        """Test adding a staff member with missing required field."""
        invalid_data = self.test_staff_data.copy()
        del invalid_data['name']
        
        with self.assertRaises(ValueError):
            self.service.add_staff_member(invalid_data)
    
    def test_update_staff_member(self):
        """Test updating a staff member's information."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        updates = {
            'name': 'John Smith',
            'email': 'john.smith@hospital.com'
        }
        
        updated_profile = self.service.update_staff_member(staff_id, updates)
        
        self.assertEqual(updated_profile['name'], 'John Smith')
        self.assertEqual(updated_profile['contact']['email'], 'john.smith@hospital.com')
    
    def test_add_skill(self):
        """Test adding a skill to a staff member."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        self.service.add_skill(staff_id, 'Surgery', SkillLevel.SENIOR)
        
        profile = self.service.get_staff_member(staff_id)
        self.assertIn('Surgery', profile['skills'])
        self.assertEqual(profile['skills']['Surgery'], SkillLevel.SENIOR)
    
    def test_add_certification(self):
        """Test adding a certification to a staff member."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        self.service.add_certification(staff_id, 'Advanced Life Support')
        
        profile = self.service.get_staff_member(staff_id)
        self.assertIn('Advanced Life Support', profile['certifications'])
    
    def test_update_availability(self):
        """Test updating staff availability."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        # Add regular availability (Monday and Tuesday)
        regular_days = {0, 1}  # Monday and Tuesday
        self.service.update_availability(staff_id, 'regular', regular_days, True)
        
        # Add exception (unavailable next Monday)
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        self.service.update_availability(staff_id, 'exception', {next_monday}, False)
        
        profile = self.service.get_staff_member(staff_id)
        self.assertEqual(profile['availability']['regular'], regular_days)
        self.assertIn(next_monday, profile['availability']['exceptions']['unavailable'])
    
    def test_update_preferences(self):
        """Test updating staff preferences."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        shift_preferences = {'DAY', 'EVENING'}
        self.service.update_preferences(staff_id, 'shift_types', shift_preferences)
        
        profile = self.service.get_staff_member(staff_id)
        self.assertEqual(profile['preferences']['shift_types'], shift_preferences)
    
    def test_assign_to_team(self):
        """Test assigning staff to a team."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        # Change team
        new_team = 'TeamB'
        self.service.assign_to_team(staff_id, new_team)
        
        profile = self.service.get_staff_member(staff_id)
        self.assertEqual(profile['team'], new_team)
        
        team_members = self.service.get_team_members(new_team)
        self.assertIn(profile, team_members)
    
    def test_get_available_staff(self):
        """Test getting available staff for a given date and shift type."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        # Set availability for Monday
        self.service.update_availability(staff_id, 'regular', {0}, True)
        
        # Set shift preference
        self.service.update_preferences(staff_id, 'shift_types', {'DAY'})
        
        # Get next Monday
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        
        # Test availability
        available_staff = self.service.get_available_staff(next_monday, 'DAY')
        self.assertEqual(len(available_staff), 1)
        self.assertEqual(available_staff[0]['id'], staff_id)
    
    def test_get_staff_with_skill(self):
        """Test getting staff with a specific skill level."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        self.service.add_skill(staff_id, 'Surgery', SkillLevel.SENIOR)
        
        # Test getting staff with minimum skill level
        qualified_staff = self.service.get_staff_with_skill('Surgery', SkillLevel.JUNIOR)
        self.assertEqual(len(qualified_staff), 1)
        self.assertEqual(qualified_staff[0]['id'], staff_id)
        
        # Test getting staff with higher minimum skill level
        qualified_staff = self.service.get_staff_with_skill('Surgery', SkillLevel.EXPERT)
        self.assertEqual(len(qualified_staff), 0)
    
    def test_get_staff_with_certification(self):
        """Test getting staff with a specific certification."""
        staff_id = self.service.add_staff_member(self.test_staff_data)
        
        self.service.add_certification(staff_id, 'Advanced Life Support')
        
        certified_staff = self.service.get_staff_with_certification('Advanced Life Support')
        self.assertEqual(len(certified_staff), 1)
        self.assertEqual(certified_staff[0]['id'], staff_id)
    
    def test_get_team_members(self):
        """Test getting all members of a team."""
        staff1_data = self.test_staff_data.copy()
        staff2_data = self.test_staff_data.copy()
        staff2_data['name'] = 'Jane Doe'
        staff2_data['email'] = 'jane@hospital.com'
        
        staff1_id = self.service.add_staff_member(staff1_data)
        staff2_id = self.service.add_staff_member(staff2_data)
        
        team_members = self.service.get_team_members('TeamA')
        self.assertEqual(len(team_members), 2)
        self.assertTrue(any(m['name'] == 'John Doe' for m in team_members))
        self.assertTrue(any(m['name'] == 'Jane Doe' for m in team_members))

if __name__ == '__main__':
    unittest.main() 