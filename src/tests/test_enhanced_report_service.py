import unittest
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import base64
from PIL import Image
from io import BytesIO

from ..services.enhanced_report_service import EnhancedReportService

class TestEnhancedReportService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.report_service = EnhancedReportService()
        self.test_schedule = self._create_test_schedule()
    
    def _create_test_schedule(self):
        """Create a test schedule with known properties"""
        start_date = datetime.now().date()
        return {
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
                        'team': 'A',
                        'preferences': ['NIGHT']
                    }
                },
                # Compliant shift
                {
                    'id': 'shift2',
                    'type': 'NIGHT',
                    'start_time': (start_date + timedelta(hours=23)).isoformat(),
                    'end_time': (start_date + timedelta(days=1, hours=7)).isoformat(),
                    'gender_requirement': 'F',
                    'assigned_staff': {
                        'id': 'staff2',
                        'gender': 'F',
                        'team': 'B',
                        'preferences': ['NIGHT']
                    }
                },
                # Regular shift
                {
                    'id': 'shift3',
                    'type': 'DAY',
                    'start_time': (start_date + timedelta(days=1)).isoformat(),
                    'end_time': (start_date + timedelta(days=1, hours=8)).isoformat(),
                    'gender_requirement': None,
                    'assigned_staff': {
                        'id': 'staff3',
                        'gender': 'M',
                        'team': 'C',
                        'preferences': ['DAY']
                    }
                }
            ]
        }

    def test_shift_distribution_analysis(self):
        """Test shift distribution analysis"""
        distribution = self.report_service._analyze_shift_distribution(self.test_schedule)
        
        # Verify structure
        self.assertIn('staff_shifts', distribution)
        self.assertIn('total_shifts', distribution)
        self.assertIn('average_shifts', distribution)
        self.assertIn('max_shifts', distribution)
        self.assertIn('min_shifts', distribution)
        self.assertIn('equity_score', distribution)
        
        # Verify calculations
        self.assertEqual(distribution['total_shifts'], 3)
        self.assertEqual(distribution['average_shifts'], 1.0)
        self.assertEqual(distribution['max_shifts'], 1)
        self.assertEqual(distribution['min_shifts'], 1)
        self.assertEqual(distribution['equity_score'], 0.0)
        
        # Verify staff shifts
        staff_shifts = distribution['staff_shifts']
        self.assertEqual(len(staff_shifts), 3)
        for staff_id, shifts in staff_shifts.items():
            self.assertEqual(shifts['total'], 1)

    def test_team_balance_analysis(self):
        """Test team balance analysis"""
        balance = self.report_service._analyze_team_balance(self.test_schedule)
        
        # Verify structure
        self.assertIn('team_shifts', balance)
        self.assertIn('total_shifts', balance)
        self.assertIn('expected_per_team', balance)
        self.assertIn('max_deviation', balance)
        self.assertIn('balance_score', balance)
        
        # Verify calculations
        self.assertEqual(balance['total_shifts'], 3)
        self.assertEqual(balance['expected_per_team'], 1.0)
        
        # Verify team shifts
        team_shifts = balance['team_shifts']
        self.assertEqual(len(team_shifts), 3)
        for team, shifts in team_shifts.items():
            self.assertEqual(shifts['total'], 1)

    def test_gender_compliance_analysis(self):
        """Test gender compliance analysis"""
        compliance = self.report_service._analyze_gender_compliance(self.test_schedule)
        
        # Verify structure
        self.assertIn('total_requirements', compliance)
        self.assertIn('met_requirements', compliance)
        self.assertIn('compliance_rate', compliance)
        self.assertIn('violations', compliance)
        
        # Verify calculations
        self.assertEqual(compliance['total_requirements'], 2)
        self.assertEqual(compliance['met_requirements'], 1)
        self.assertEqual(compliance['compliance_rate'], 0.5)
        
        # Verify violations
        violations = compliance['violations']
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation['shift_id'], 'shift1')
        self.assertEqual(violation['required'], 'F')
        self.assertEqual(violation['assigned'], 'M')

    def test_preference_satisfaction_analysis(self):
        """Test preference satisfaction analysis"""
        satisfaction = self.report_service._analyze_preference_satisfaction(self.test_schedule)
        
        # Verify structure
        self.assertIn('total_preferences', satisfaction)
        self.assertIn('met_preferences', satisfaction)
        self.assertIn('satisfaction_rate', satisfaction)
        self.assertIn('staff_satisfaction', satisfaction)
        
        # Verify calculations
        self.assertEqual(satisfaction['total_preferences'], 3)
        self.assertEqual(satisfaction['met_preferences'], 2)
        
        # Verify staff satisfaction
        staff_satisfaction = satisfaction['staff_satisfaction']
        self.assertEqual(len(staff_satisfaction), 3)
        for staff_id, stats in staff_satisfaction.items():
            self.assertIn('total', stats)
            self.assertIn('met', stats)

    def test_conflict_analysis(self):
        """Test conflict analysis"""
        conflicts = self.report_service._analyze_conflicts(self.test_schedule)
        
        # Verify structure
        self.assertIn('total_conflicts', conflicts)
        self.assertIn('conflict_types', conflicts)
        self.assertIn('severity_counts', conflicts)
        self.assertIn('affected_staff_count', conflicts)
        self.assertIn('affected_staff_percentage', conflicts)
        
        # Verify there are conflicts (at least gender requirement conflict)
        self.assertGreater(conflicts['total_conflicts'], 0)
        self.assertIn('GENDER_REQUIREMENT', conflicts['conflict_types'])

    def test_visualization_generation(self):
        """Test visualization generation"""
        visualizations = self.report_service._generate_visualizations(self.test_schedule)
        
        # Verify all visualizations are generated
        self.assertIn('shift_distribution', visualizations)
        self.assertIn('team_balance', visualizations)
        self.assertIn('gender_compliance', visualizations)
        self.assertIn('preference_satisfaction', visualizations)
        
        # Verify each visualization is a valid base64 image
        for viz_name, viz_data in visualizations.items():
            # Verify it's a valid base64 string
            try:
                image_data = base64.b64decode(viz_data)
                image = Image.open(BytesIO(image_data))
                self.assertIsNotNone(image)
            except Exception as e:
                self.fail(f"Invalid visualization for {viz_name}: {str(e)}")

    def test_excel_export(self):
        """Test Excel report export"""
        test_file = 'test_report.xlsx'
        try:
            # Generate report
            self.report_service.export_to_excel(self.test_schedule, test_file)
            
            # Verify file exists
            self.assertTrue(os.path.exists(test_file))
            
            # Verify Excel content
            with pd.ExcelFile(test_file) as excel:
                # Verify all sheets are present
                expected_sheets = [
                    'Shift Distribution',
                    'Team Balance',
                    'Gender Compliance',
                    'Preference Satisfaction',
                    'Conflict Metrics'
                ]
                for sheet in expected_sheets:
                    self.assertIn(sheet, excel.sheet_names)
                
                # Verify data in sheets
                shift_dist = pd.read_excel(excel, 'Shift Distribution')
                self.assertEqual(len(shift_dist), 3)  # 3 staff members
                
                team_balance = pd.read_excel(excel, 'Team Balance')
                self.assertEqual(len(team_balance), 3)  # 3 teams
                
                gender_compliance = pd.read_excel(excel, 'Gender Compliance')
                self.assertEqual(len(gender_compliance), 1)  # 1 violation
                
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_complete_report_generation(self):
        """Test complete report generation"""
        report = self.report_service.generate_detailed_report(self.test_schedule)
        
        # Verify all sections are present
        self.assertIn('shift_distribution', report)
        self.assertIn('team_balance', report)
        self.assertIn('gender_compliance', report)
        self.assertIn('preference_satisfaction', report)
        self.assertIn('conflict_metrics', report)
        self.assertIn('visualizations', report)
        
        # Verify each section has the expected data
        self.assertIsInstance(report['shift_distribution'], dict)
        self.assertIsInstance(report['team_balance'], dict)
        self.assertIsInstance(report['gender_compliance'], dict)
        self.assertIsInstance(report['preference_satisfaction'], dict)
        self.assertIsInstance(report['conflict_metrics'], dict)
        self.assertIsInstance(report['visualizations'], dict)

if __name__ == '__main__':
    unittest.main() 