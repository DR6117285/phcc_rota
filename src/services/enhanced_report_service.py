from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime, timedelta
import logging

from ..core.equity_tracker import EquityTracker
from ..services.conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)

class EnhancedReportService:
    def __init__(self):
        self.equity_tracker = EquityTracker()
        self.conflict_resolver = ConflictResolver()
    
    def generate_detailed_report(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive report with metrics and visualizations"""
        report = {
            'shift_distribution': self._analyze_shift_distribution(schedule),
            'team_balance': self._analyze_team_balance(schedule),
            'gender_compliance': self._analyze_gender_compliance(schedule),
            'preference_satisfaction': self._analyze_preference_satisfaction(schedule),
            'conflict_metrics': self._analyze_conflicts(schedule),
            'visualizations': self._generate_visualizations(schedule)
        }
        return report
    
    def _analyze_shift_distribution(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze shift distribution across staff"""
        shifts = schedule['shifts']
        staff_shifts = {}
        
        for shift in shifts:
            staff_id = shift['assigned_staff']['id']
            shift_type = shift['type']
            
            if staff_id not in staff_shifts:
                staff_shifts[staff_id] = {'total': 0}
            
            staff_shifts[staff_id]['total'] += 1
            staff_shifts[staff_id][shift_type] = staff_shifts[staff_id].get(shift_type, 0) + 1
        
        # Calculate equity metrics
        total_shifts = len(shifts)
        avg_shifts = total_shifts / len(staff_shifts) if staff_shifts else 0
        max_shifts = max(s['total'] for s in staff_shifts.values()) if staff_shifts else 0
        min_shifts = min(s['total'] for s in staff_shifts.values()) if staff_shifts else 0
        
        return {
            'staff_shifts': staff_shifts,
            'total_shifts': total_shifts,
            'average_shifts': avg_shifts,
            'max_shifts': max_shifts,
            'min_shifts': min_shifts,
            'equity_score': (max_shifts - min_shifts) / avg_shifts if avg_shifts else 0
        }
    
    def _analyze_team_balance(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze team balance across shifts"""
        shifts = schedule['shifts']
        team_shifts = {}
        
        for shift in shifts:
            team = shift['assigned_staff']['team']
            shift_type = shift['type']
            
            if team not in team_shifts:
                team_shifts[team] = {'total': 0}
            
            team_shifts[team]['total'] += 1
            team_shifts[team][shift_type] = team_shifts[team].get(shift_type, 0) + 1
        
        # Calculate balance metrics
        total_shifts = len(shifts)
        teams = list(team_shifts.keys())
        expected_per_team = total_shifts / len(teams) if teams else 0
        max_deviation = max(abs(t['total'] - expected_per_team) for t in team_shifts.values()) if teams else 0
        
        return {
            'team_shifts': team_shifts,
            'total_shifts': total_shifts,
            'expected_per_team': expected_per_team,
            'max_deviation': max_deviation,
            'balance_score': 1 - (max_deviation / expected_per_team) if expected_per_team else 0
        }
    
    def _analyze_gender_compliance(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze gender requirement compliance"""
        shifts = schedule['shifts']
        total_requirements = 0
        met_requirements = 0
        violations = []
        
        for shift in shifts:
            if shift.get('gender_requirement'):
                total_requirements += 1
                staff_gender = shift['assigned_staff']['gender']
                if staff_gender == shift['gender_requirement']:
                    met_requirements += 1
                else:
                    violations.append({
                        'shift_id': shift['id'],
                        'required': shift['gender_requirement'],
                        'assigned': staff_gender
                    })
        
        return {
            'total_requirements': total_requirements,
            'met_requirements': met_requirements,
            'compliance_rate': met_requirements / total_requirements if total_requirements else 1.0,
            'violations': violations
        }
    
    def _analyze_preference_satisfaction(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze staff preference satisfaction"""
        shifts = schedule['shifts']
        total_preferences = 0
        met_preferences = 0
        staff_satisfaction = {}
        
        for shift in shifts:
            staff = shift['assigned_staff']
            if 'preferences' in staff:
                total_preferences += 1
                if shift['type'] in staff['preferences']:
                    met_preferences += 1
                    
                staff_id = staff['id']
                if staff_id not in staff_satisfaction:
                    staff_satisfaction[staff_id] = {
                        'total': 0,
                        'met': 0
                    }
                staff_satisfaction[staff_id]['total'] += 1
                if shift['type'] in staff['preferences']:
                    staff_satisfaction[staff_id]['met'] += 1
        
        return {
            'total_preferences': total_preferences,
            'met_preferences': met_preferences,
            'satisfaction_rate': met_preferences / total_preferences if total_preferences else 1.0,
            'staff_satisfaction': staff_satisfaction
        }
    
    def _analyze_conflicts(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conflicts in the schedule"""
        conflicts = self.conflict_resolver.detect_conflicts(schedule)
        
        conflict_types = {}
        severity_counts = {}
        affected_staff = set()
        
        for conflict in conflicts:
            # Count conflict types
            conflict_type = conflict.conflict_type.value
            conflict_types[conflict_type] = conflict_types.get(conflict_type, 0) + 1
            
            # Count severities
            severity = conflict.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Track affected staff
            affected_staff.update(conflict.affected_staff)
        
        return {
            'total_conflicts': len(conflicts),
            'conflict_types': conflict_types,
            'severity_counts': severity_counts,
            'affected_staff_count': len(affected_staff),
            'affected_staff_percentage': len(affected_staff) / len(set(s['assigned_staff']['id'] for s in schedule['shifts']))
        }
    
    def _generate_visualizations(self, schedule: Dict[str, Any]) -> Dict[str, str]:
        """Generate visualizations for the report"""
        visualizations = {}
        
        # Shift distribution visualization
        visualizations['shift_distribution'] = self._create_shift_distribution_chart(schedule)
        
        # Team balance visualization
        visualizations['team_balance'] = self._create_team_balance_chart(schedule)
        
        # Gender compliance visualization
        visualizations['gender_compliance'] = self._create_gender_compliance_chart(schedule)
        
        # Preference satisfaction visualization
        visualizations['preference_satisfaction'] = self._create_preference_satisfaction_chart(schedule)
        
        return visualizations
    
    def _create_shift_distribution_chart(self, schedule: Dict[str, Any]) -> str:
        """Create shift distribution visualization"""
        distribution = self._analyze_shift_distribution(schedule)
        df = pd.DataFrame.from_dict(distribution['staff_shifts'], orient='index')
        
        plt.figure(figsize=(10, 6))
        df.plot(kind='bar', stacked=True)
        plt.title('Shift Distribution by Staff')
        plt.xlabel('Staff ID')
        plt.ylabel('Number of Shifts')
        plt.legend(title='Shift Type')
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _create_team_balance_chart(self, schedule: Dict[str, Any]) -> str:
        """Create team balance visualization"""
        balance = self._analyze_team_balance(schedule)
        df = pd.DataFrame.from_dict(balance['team_shifts'], orient='index')
        
        plt.figure(figsize=(10, 6))
        df.plot(kind='bar', stacked=True)
        plt.title('Shift Distribution by Team')
        plt.xlabel('Team')
        plt.ylabel('Number of Shifts')
        plt.legend(title='Shift Type')
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _create_gender_compliance_chart(self, schedule: Dict[str, Any]) -> str:
        """Create gender compliance visualization"""
        compliance = self._analyze_gender_compliance(schedule)
        
        plt.figure(figsize=(8, 8))
        plt.pie([compliance['met_requirements'], 
                compliance['total_requirements'] - compliance['met_requirements']],
               labels=['Compliant', 'Non-compliant'],
               autopct='%1.1f%%')
        plt.title('Gender Requirement Compliance')
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _create_preference_satisfaction_chart(self, schedule: Dict[str, Any]) -> str:
        """Create preference satisfaction visualization"""
        satisfaction = self._analyze_preference_satisfaction(schedule)
        staff_satisfaction = satisfaction['staff_satisfaction']
        
        satisfaction_rates = []
        for staff_id, stats in staff_satisfaction.items():
            rate = stats['met'] / stats['total'] if stats['total'] > 0 else 0
            satisfaction_rates.append(rate)
        
        plt.figure(figsize=(10, 6))
        plt.hist(satisfaction_rates, bins=10, range=(0, 1))
        plt.title('Staff Preference Satisfaction Distribution')
        plt.xlabel('Satisfaction Rate')
        plt.ylabel('Number of Staff')
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _fig_to_base64(self) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode()

    def export_to_excel(self, schedule: Dict[str, Any], filepath: str):
        """Export detailed report to Excel"""
        report = self.generate_detailed_report(schedule)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Shift Distribution Sheet
            pd.DataFrame.from_dict(report['shift_distribution']['staff_shifts'], 
                                 orient='index').to_excel(writer, sheet_name='Shift Distribution')
            
            # Team Balance Sheet
            pd.DataFrame.from_dict(report['team_balance']['team_shifts'],
                                 orient='index').to_excel(writer, sheet_name='Team Balance')
            
            # Gender Compliance Sheet
            pd.DataFrame(report['gender_compliance']['violations']).to_excel(
                writer, sheet_name='Gender Compliance')
            
            # Preference Satisfaction Sheet
            pd.DataFrame.from_dict(report['preference_satisfaction']['staff_satisfaction'],
                                 orient='index').to_excel(writer, sheet_name='Preference Satisfaction')
            
            # Conflict Metrics Sheet
            conflict_data = {
                'Conflict Types': pd.Series(report['conflict_metrics']['conflict_types']),
                'Severity Counts': pd.Series(report['conflict_metrics']['severity_counts'])
            }
            pd.DataFrame(conflict_data).to_excel(writer, sheet_name='Conflict Metrics') 