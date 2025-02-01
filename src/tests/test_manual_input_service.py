import unittest
import json
import tempfile
import os
from datetime import datetime, date
import pandas as pd

from ..services.manual_input_service import ManualInputService

class TestManualInputService(unittest.TestCase):
    def setUp(self):
        self.service = ManualInputService()
        self.test_data = {
            'staff': [
                {
                    'staff_id': 'S001',
                    'name': 'John Doe',
                    'gender': 'M',
                    'team': 'TeamA',
                    'preferences': [
                        {
                            'date': '2024-01-01',
                            'shift_type': 'MORNING'
                        }
                    ],
                    'leave_dates': ['2024-01-15', '2024-01-16']
                },
                {
                    'staff_id': 'S002',
                    'name': 'Jane Smith',
                    'gender': 'F',
                    'team': 'TeamB',
                    'preferences': [],
                    'leave_dates': []
                }
            ]
        }

    def test_json_import(self):
        """Test importing data from JSON file"""
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file = f.name

        try:
            staff_data = self.service.import_staff_data(temp_file)
            self.assertEqual(len(staff_data), 2)
            self.assertEqual(staff_data[0]['staff_id'], 'S001')
            self.assertEqual(staff_data[1]['name'], 'Jane Smith')
        finally:
            os.unlink(temp_file)

    def test_csv_import(self):
        """Test importing data from CSV file"""
        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', newline='', delete=False) as f:
            import csv
            fieldnames = ['staff_id', 'name', 'gender', 'team', 'preferences', 'leave_dates']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for staff in self.test_data['staff']:
                staff['preferences'] = json.dumps(staff['preferences'])
                staff['leave_dates'] = json.dumps(staff['leave_dates'])
                writer.writerow(staff)
            
            temp_file = f.name

        try:
            staff_data = self.service.import_staff_data(temp_file)
            self.assertEqual(len(staff_data), 2)
            self.assertEqual(staff_data[0]['staff_id'], 'S001')
            self.assertEqual(staff_data[1]['name'], 'Jane Smith')
        finally:
            os.unlink(temp_file)

    def test_excel_import(self):
        """Test importing data from Excel file"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_file = f.name

        try:
            # Create Excel file with multiple sheets
            with pd.ExcelWriter(temp_file) as writer:
                # Staff sheet
                staff_df = pd.DataFrame([
                    {k: v for k, v in staff.items() if k not in ['preferences', 'leave_dates']}
                    for staff in self.test_data['staff']
                ])
                staff_df.to_excel(writer, sheet_name='Staff', index=False)
                
                # Preferences sheet
                preferences = []
                for staff in self.test_data['staff']:
                    for pref in staff['preferences']:
                        preferences.append({
                            'staff_id': staff['staff_id'],
                            **pref
                        })
                pd.DataFrame(preferences).to_excel(writer, sheet_name='Preferences', index=False)
                
                # Leave sheet
                leave_data = []
                for staff in self.test_data['staff']:
                    for leave_date in staff['leave_dates']:
                        leave_data.append({
                            'staff_id': staff['staff_id'],
                            'date': leave_date
                        })
                pd.DataFrame(leave_data).to_excel(writer, sheet_name='Leave', index=False)

            staff_data = self.service.import_staff_data(temp_file)
            self.assertEqual(len(staff_data), 2)
            self.assertEqual(staff_data[0]['staff_id'], 'S001')
            self.assertEqual(staff_data[1]['name'], 'Jane Smith')
        finally:
            os.unlink(temp_file)

    def test_shift_preferences_import(self):
        """Test importing shift preferences"""
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file = f.name

        try:
            preferences = self.service.import_shift_preferences(temp_file)
            self.assertIn('S001', preferences)
            self.assertEqual(len(preferences['S001']), 1)
            self.assertEqual(preferences['S001'][0]['shift_type'], 'MORNING')
            self.assertIsInstance(preferences['S001'][0]['date'], date)
        finally:
            os.unlink(temp_file)

    def test_leave_data_import(self):
        """Test importing leave data"""
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file = f.name

        try:
            leave_data = self.service.import_leave_data(temp_file)
            self.assertIn('S001', leave_data)
            self.assertEqual(len(leave_data['S001']), 2)
            self.assertIsInstance(leave_data['S001'][0], date)
        finally:
            os.unlink(temp_file)

    def test_team_assignments_import(self):
        """Test importing team assignments"""
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            json.dump(self.test_data, f)
            temp_file = f.name

        try:
            team_assignments = self.service.import_team_assignments(temp_file)
            self.assertEqual(team_assignments['S001'], 'TeamA')
            self.assertEqual(team_assignments['S002'], 'TeamB')
        finally:
            os.unlink(temp_file)

    def test_validation(self):
        """Test data validation"""
        invalid_data = {
            'staff': [
                {
                    'name': 'Invalid Staff',  # Missing staff_id
                    'gender': 'M'
                },
                {
                    'staff_id': 123,  # Invalid type
                    'name': 'Type Error',
                    'gender': 'F',
                    'preferences': 'invalid'  # Invalid type
                }
            ]
        }
        
        errors = self.service.validate_import(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('Missing required fields' in error for error in errors))
        self.assertTrue(any('Invalid staff_id type' in error for error in errors))
        self.assertTrue(any('Invalid preferences format' in error for error in errors))

    def test_unsupported_format(self):
        """Test handling of unsupported file formats"""
        with self.assertRaises(ValueError):
            self.service.import_staff_data('invalid.txt')

if __name__ == '__main__':
    unittest.main() 