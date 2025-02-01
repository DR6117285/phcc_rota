from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import logging
from collections import defaultdict

from ..interfaces.conflict_interfaces import (
    IConflictResolver, Conflict, ConflictType,
    ConflictSeverity, ConflictResolution
)
from ..core.equity_tracker import EquityTracker
from ..services.data_loader import StaffDataLoader

logger = logging.getLogger(__name__)

class ConflictResolver(IConflictResolver):
    def __init__(self, staff_loader: StaffDataLoader):
        self.resolution_history = []
        self.staff_loader = staff_loader
        self.equity_tracker = EquityTracker()
        
    def detect_conflicts(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Detect all conflicts in the schedule"""
        conflicts = []
        
        # Check each type of conflict
        conflicts.extend(self._check_gender_requirements(schedule))
        conflicts.extend(self._check_consecutive_shifts(schedule))
        conflicts.extend(self._check_team_balance(schedule))
        conflicts.extend(self._check_staff_availability(schedule))
        conflicts.extend(self._check_preferences(schedule))
        conflicts.extend(self._check_workload_balance(schedule))
        
        return conflicts
    
    def analyze_conflict(self, conflict: Conflict) -> Dict[str, Any]:
        """Provide detailed analysis of a specific conflict"""
        analysis = {
            'type': conflict.conflict_type.value,
            'severity': conflict.severity.value,
            'description': conflict.description,
            'affected_shifts': len(conflict.affected_shifts),
            'affected_staff': len(conflict.affected_staff),
            'metrics': conflict.metrics,
            'impact_analysis': self._analyze_impact(conflict),
            'resolution_options': len(conflict.possible_resolutions),
            'historical_context': self._get_historical_context(conflict)
        }
        
        return analysis
    
    def suggest_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest possible resolutions for a conflict"""
        resolutions = []
        
        if conflict.conflict_type == ConflictType.GENDER_REQUIREMENT:
            resolutions.extend(self._suggest_gender_resolutions(conflict))
        elif conflict.conflict_type == ConflictType.CONSECUTIVE_SHIFTS:
            resolutions.extend(self._suggest_consecutive_resolutions(conflict))
        elif conflict.conflict_type == ConflictType.TEAM_BALANCE:
            resolutions.extend(self._suggest_team_balance_resolutions(conflict))
        elif conflict.conflict_type == ConflictType.STAFF_UNAVAILABLE:
            resolutions.extend(self._suggest_availability_resolutions(conflict))
        elif conflict.conflict_type == ConflictType.PREFERENCE_VIOLATION:
            resolutions.extend(self._suggest_preference_resolutions(conflict))
        elif conflict.conflict_type == ConflictType.WORKLOAD_IMBALANCE:
            resolutions.extend(self._suggest_workload_resolutions(conflict))
        
        return resolutions
    
    def apply_resolution(self, conflict: Conflict, resolution: Dict[str, Any]) -> bool:
        """Apply a selected resolution to the schedule"""
        try:
            resolution_type = ConflictResolution(resolution['type'])
            
            if resolution_type == ConflictResolution.SWAP_STAFF:
                success = self._apply_staff_swap(conflict, resolution)
            elif resolution_type == ConflictResolution.REASSIGN_SHIFT:
                success = self._apply_shift_reassignment(conflict, resolution)
            elif resolution_type == ConflictResolution.OVERRIDE_CONSTRAINT:
                success = self._apply_constraint_override(conflict, resolution)
            elif resolution_type == ConflictResolution.MANUAL_RESOLVE:
                success = self._apply_manual_resolution(conflict, resolution)
            
            if success:
                self._record_resolution(conflict, resolution)
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying resolution: {str(e)}")
            return False
    
    def get_distribution_metrics(self, 
                               schedule: Dict[str, Any],
                               start_date: date,
                               end_date: date) -> Dict[str, Any]:
        """Get shift distribution metrics for a date range"""
        metrics = {
            'shift_counts': self._get_shift_counts(schedule, start_date, end_date),
            'team_distribution': self._get_team_distribution(schedule, start_date, end_date),
            'gender_distribution': self._get_gender_distribution(schedule, start_date, end_date),
            'workload_metrics': self._get_workload_metrics(schedule, start_date, end_date),
            'preference_satisfaction': self._get_preference_satisfaction(schedule, start_date, end_date)
        }
        return metrics
    
    def validate_manual_resolution(self, 
                                 conflict: Conflict,
                                 proposed_changes: Dict[str, Any]) -> List[str]:
        """Validate proposed manual changes"""
        errors = []
        
        # Check required fields
        if 'affected_shifts' not in proposed_changes:
            errors.append("Missing required field: affected_shifts")
        if 'new_assignments' not in proposed_changes:
            errors.append("Missing required field: new_assignments")
            
        if errors:
            return errors
            
        # Validate shift IDs
        for shift_id in proposed_changes['affected_shifts']:
            if not any(s['id'] == shift_id for s in conflict.affected_shifts):
                errors.append(f"Invalid shift ID: {shift_id}")
                
        # Validate staff assignments
        all_staff = {s.id for s in self.staff_loader.load_all_staff()}
        for shift_id, staff_id in proposed_changes['new_assignments'].items():
            if staff_id not in all_staff:
                errors.append(f"Invalid staff ID: {staff_id}")
                
        return errors
    
    def get_staff_impact(self, 
                        conflict: Conflict,
                        resolution: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact of resolution on affected staff"""
        impact = {
            'directly_affected': self._get_directly_affected(conflict, resolution),
            'indirectly_affected': self._get_indirectly_affected(conflict, resolution),
            'workload_changes': self._get_workload_impact(conflict, resolution),
            'preference_impact': self._get_preference_impact(conflict, resolution)
        }
        
        return impact
    
    def get_resolution_history(self, 
                             schedule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get history of applied conflict resolutions"""
        return self.resolution_history
    
    def _check_gender_requirements(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Check for gender requirement conflicts"""
        conflicts = []
        
        for shift in schedule['shifts']:
            if shift['gender_requirement']:
                staff = shift['assigned_staff']
                if staff['gender'] != shift['gender_requirement']:
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.GENDER_REQUIREMENT,
                        severity=ConflictSeverity.CRITICAL,
                        description=f"Gender requirement mismatch for shift {shift['id']}",
                        affected_shifts=[shift],
                        affected_staff=[staff['id']],
                        possible_resolutions=[],
                        metrics={'required_gender': shift['gender_requirement']}
                    ))
        
        return conflicts
    
    def _check_consecutive_shifts(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Check for consecutive shift violations"""
        conflicts = []
        staff_shifts = defaultdict(list)
        
        # Group shifts by staff
        for shift in schedule['shifts']:
            staff_shifts[shift['assigned_staff']['id']].append(shift)
        
        # Check consecutive shifts
        for staff_id, shifts in staff_shifts.items():
            sorted_shifts = sorted(shifts, key=lambda x: x['start_time'])
            for i in range(len(sorted_shifts) - 1):
                end_time = datetime.fromisoformat(sorted_shifts[i]['end_time'])
                start_time = datetime.fromisoformat(sorted_shifts[i + 1]['start_time'])
                rest_period = (start_time - end_time).total_seconds() / 3600
                
                if rest_period < 8:  # Less than 8 hours between shifts
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.CONSECUTIVE_SHIFTS,
                        severity=ConflictSeverity.HIGH,
                        description=f"Insufficient rest period ({rest_period:.1f} hours)",
                        affected_shifts=[sorted_shifts[i], sorted_shifts[i + 1]],
                        affected_staff=[staff_id],
                        possible_resolutions=[],
                        metrics={'rest_period': rest_period}
                    ))
        
        return conflicts
    
    def _check_team_balance(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Check for team balance conflicts"""
        conflicts = []
        shift_teams = defaultdict(lambda: defaultdict(int))
        
        # Count shifts by team for each shift type
        for shift in schedule['shifts']:
            shift_type = shift['type']
            team = shift['assigned_staff']['team']
            shift_teams[shift_type][team] += 1
        
        # Check balance for each shift type
        for shift_type, team_counts in shift_teams.items():
            if team_counts:
                min_shifts = min(team_counts.values())
                max_shifts = max(team_counts.values())
                if max_shifts - min_shifts > 2:  # More than 2 shifts difference
                    conflicts.append(Conflict(
                        conflict_type=ConflictType.TEAM_BALANCE,
                        severity=ConflictSeverity.MEDIUM,
                        description=f"Team imbalance in {shift_type} shifts",
                        affected_shifts=[],  # Would need to find specific shifts
                        affected_staff=[],   # Would need to identify staff
                        possible_resolutions=[],
                        metrics={'team_counts': dict(team_counts)}
                    ))
        
        return conflicts
    
    def _check_staff_availability(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Check for staff availability conflicts"""
        conflicts = []
        
        for shift in schedule['shifts']:
            staff = shift['assigned_staff']
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            
            if shift_date in staff.get('leave_dates', []):
                conflicts.append(Conflict(
                    conflict_type=ConflictType.STAFF_UNAVAILABLE,
                    severity=ConflictSeverity.CRITICAL,
                    description=f"Staff on leave during shift",
                    affected_shifts=[shift],
                    affected_staff=[staff['id']],
                    possible_resolutions=[],
                    metrics={'leave_date': shift_date.isoformat()}
                ))
        
        return conflicts
    
    def _check_preferences(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Check for preference violations"""
        conflicts = []
        
        for shift in schedule['shifts']:
            staff = shift['assigned_staff']
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            
            # Check if staff had a different preference for this date
            staff_preferences = staff.get('preferences', {}).get(shift_date, [])
            if staff_preferences and shift['type'] not in staff_preferences:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.PREFERENCE_VIOLATION,
                    severity=ConflictSeverity.LOW,
                    description=f"Shift does not match staff preference",
                    affected_shifts=[shift],
                    affected_staff=[staff['id']],
                    possible_resolutions=[],
                    metrics={
                        'preferred_shifts': staff_preferences,
                        'assigned_shift': shift['type']
                    }
                ))
        
        return conflicts
    
    def _check_workload_balance(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Check for workload imbalance"""
        conflicts = []
        staff_shifts = defaultdict(int)
        
        # Count total shifts per staff
        for shift in schedule['shifts']:
            staff_shifts[shift['assigned_staff']['id']] += 1
        
        if staff_shifts:
            min_shifts = min(staff_shifts.values())
            max_shifts = max(staff_shifts.values())
            if max_shifts - min_shifts > 4:  # More than 4 shifts difference
                conflicts.append(Conflict(
                    conflict_type=ConflictType.WORKLOAD_IMBALANCE,
                    severity=ConflictSeverity.HIGH,
                    description="Significant workload imbalance between staff",
                    affected_shifts=[],  # Would need to identify specific shifts
                    affected_staff=list(staff_shifts.keys()),
                    possible_resolutions=[],
                    metrics={'shift_counts': dict(staff_shifts)}
                ))
        
        return conflicts
    
    def _suggest_gender_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest resolutions for gender requirement conflicts"""
        resolutions = []
        shift = conflict.affected_shifts[0]
        
        # Suggest staff swaps
        resolutions.append({
            'type': ConflictResolution.SWAP_STAFF.value,
            'description': 'Swap with eligible staff member',
            'details': {
                'shift_id': shift['id'],
                'current_staff': shift['assigned_staff']['id'],
                'eligible_staff': self._find_eligible_staff(shift)
            }
        })
        
        # Suggest shift reassignment
        resolutions.append({
            'type': ConflictResolution.REASSIGN_SHIFT.value,
            'description': 'Reassign shift to eligible staff',
            'details': {
                'shift_id': shift['id'],
                'eligible_staff': self._find_eligible_staff(shift)
            }
        })
        
        return resolutions
    
    def _find_eligible_staff(self, shift: Dict[str, Any]) -> List[str]:
        """Find eligible staff for a shift based on requirements"""
        all_staff = self.staff_loader.load_all_staff()
        eligible_staff = []
        
        for staff in all_staff:
            # Check gender requirement
            if shift['gender_requirement'] and staff.gender != shift['gender_requirement']:
                continue
                
            # Check availability
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            if shift_date in staff.leave_dates:
                continue
                
            # Check consecutive shifts
            if self._would_create_consecutive_violation(staff.id, shift):
                continue
                
            # Check workload balance
            if self._would_create_workload_imbalance(staff.id, shift):
                continue
                
            eligible_staff.append(staff.id)
            
        return eligible_staff
    
    def _record_resolution(self, conflict: Conflict, resolution: Dict[str, Any]):
        """Record an applied resolution in history"""
        self.resolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'conflict_type': conflict.conflict_type.value,
            'resolution_type': resolution['type'],
            'affected_shifts': [s['id'] for s in conflict.affected_shifts],
            'affected_staff': conflict.affected_staff,
            'description': resolution['description']
        })
    
    def _get_shift_counts(self, 
                         schedule: Dict[str, Any],
                         start_date: date,
                         end_date: date) -> Dict[str, Any]:
        """Get shift distribution counts"""
        counts = defaultdict(lambda: defaultdict(int))
        
        for shift in schedule['shifts']:
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            if start_date <= shift_date <= end_date:
                staff_id = shift['assigned_staff']['id']
                shift_type = shift['type']
                counts[staff_id][shift_type] += 1
                
        return dict(counts)
    
    def _validate_specific_changes(self, 
                                 conflict: Conflict,
                                 proposed_changes: Dict[str, Any]) -> List[str]:
        """Validate specific aspects of proposed changes"""
        errors = []
        
        # Validate staff assignments
        for shift_id, new_staff_id in proposed_changes['new_assignments'].items():
            if not self._is_staff_eligible(shift_id, new_staff_id):
                errors.append(
                    f"Staff {new_staff_id} not eligible for shift {shift_id}"
                )
        
        return errors
    
    def _is_staff_eligible(self, shift_id: str, staff_id: str) -> bool:
        """Check if staff member is eligible for a shift"""
        # This would be implemented to check all eligibility criteria
        return True  # Placeholder
    
    def _suggest_consecutive_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest resolutions for consecutive shift conflicts"""
        resolutions = []
        shifts = conflict.affected_shifts
        
        # Suggest swapping one of the shifts
        for shift in shifts:
            resolutions.append({
                'type': ConflictResolution.SWAP_STAFF.value,
                'description': f'Swap shift {shift["id"]} with another staff member',
                'details': {
                    'shift_id': shift['id'],
                    'current_staff': shift['assigned_staff']['id'],
                    'eligible_staff': self._find_eligible_staff(shift)
                }
            })
        
        return resolutions
    
    def _suggest_team_balance_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest resolutions for team balance conflicts"""
        resolutions = []
        metrics = conflict.metrics
        
        # Find teams with too many/few shifts
        team_counts = metrics['team_counts']
        max_team = max(team_counts.items(), key=lambda x: x[1])[0]
        min_team = min(team_counts.items(), key=lambda x: x[1])[0]
        
        resolutions.append({
            'type': ConflictResolution.REASSIGN_SHIFT.value,
            'description': f'Reassign shift from {max_team} to {min_team}',
            'details': {
                'from_team': max_team,
                'to_team': min_team,
                'shift_count_difference': team_counts[max_team] - team_counts[min_team]
            }
        })
        
        return resolutions
    
    def _suggest_availability_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest resolutions for staff availability conflicts"""
        shift = conflict.affected_shifts[0]
        
        return [{
            'type': ConflictResolution.REASSIGN_SHIFT.value,
            'description': 'Reassign shift to available staff member',
            'details': {
                'shift_id': shift['id'],
                'current_staff': shift['assigned_staff']['id'],
                'eligible_staff': self._find_eligible_staff(shift)
            }
        }]
    
    def _suggest_preference_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest resolutions for preference violations"""
        shift = conflict.affected_shifts[0]
        metrics = conflict.metrics
        
        resolutions = [{
            'type': ConflictResolution.SWAP_STAFF.value,
            'description': 'Swap with staff member who prefers this shift',
            'details': {
                'shift_id': shift['id'],
                'current_staff': shift['assigned_staff']['id'],
                'preferred_shifts': metrics['preferred_shifts']
            }
        }]
        
        # Option to override if no better solution
        resolutions.append({
            'type': ConflictResolution.OVERRIDE_CONSTRAINT.value,
            'description': 'Keep current assignment (override preference)',
            'details': {
                'constraint_type': 'preference',
                'impact': 'low'
            }
        })
        
        return resolutions
    
    def _suggest_workload_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest resolutions for workload imbalance"""
        metrics = conflict.metrics
        shift_counts = metrics['shift_counts']
        
        # Find staff with most/least shifts
        max_staff = max(shift_counts.items(), key=lambda x: x[1])[0]
        min_staff = min(shift_counts.items(), key=lambda x: x[1])[0]
        
        return [{
            'type': ConflictResolution.REASSIGN_SHIFT.value,
            'description': f'Reassign shift from {max_staff} to {min_staff}',
            'details': {
                'from_staff': max_staff,
                'to_staff': min_staff,
                'shift_difference': shift_counts[max_staff] - shift_counts[min_staff]
            }
        }]
    
    def _apply_staff_swap(self, conflict: Conflict, resolution: Dict[str, Any]) -> bool:
        """Apply a staff swap resolution"""
        try:
            shift_id = resolution['details']['shift_id']
            new_staff_id = resolution['details']['new_staff_id']
            
            # Find the shift in the schedule
            for shift in conflict.affected_shifts:
                if shift['id'] == shift_id:
                    # Store old staff for swap
                    old_staff = shift['assigned_staff']
                    
                    # Find the new staff member's current shift if any
                    new_staff_shift = None
                    for s in conflict.affected_shifts:
                        if s['assigned_staff']['id'] == new_staff_id:
                            new_staff_shift = s
                            break
                    
                    # Perform the swap
                    if new_staff_shift:
                        # Swap staff between shifts
                        new_staff_shift['assigned_staff'] = old_staff
                    
                    # Update the target shift
                    shift['assigned_staff'] = {
                        'id': new_staff_id,
                        'gender': resolution['details'].get('new_staff_gender', 'F'),  # Default to F for gender requirements
                        'team': resolution['details'].get('new_staff_team', old_staff['team']),
                        'leave_dates': []  # Reset leave dates for new assignment
                    }
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying staff swap: {str(e)}")
            return False
    
    def _apply_shift_reassignment(self, conflict: Conflict, resolution: Dict[str, Any]) -> bool:
        """Apply a shift reassignment resolution"""
        try:
            shift_id = resolution['details']['shift_id']
            new_staff_id = resolution['details']['new_staff_id']
            
            # Find the shift in the schedule
            for shift in conflict.affected_shifts:
                if shift['id'] == shift_id:
                    # Update the shift assignment
                    shift['assigned_staff'] = {
                        'id': new_staff_id,
                        'gender': resolution['details'].get('new_staff_gender', 'F'),
                        'team': resolution['details'].get('new_staff_team', 'A'),
                        'leave_dates': []
                    }
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying shift reassignment: {str(e)}")
            return False
    
    def _apply_constraint_override(self, conflict: Conflict, resolution: Dict[str, Any]) -> bool:
        """Apply a constraint override resolution"""
        try:
            constraint_type = resolution['details']['constraint_type']
            shift_id = resolution['details'].get('shift_id')
            
            # Find the affected shift
            for shift in conflict.affected_shifts:
                if shift['id'] == shift_id:
                    if constraint_type == 'gender_requirement':
                        # Remove gender requirement
                        shift['gender_requirement'] = None
                    elif constraint_type == 'consecutive_shifts':
                        # Mark shift as override_consecutive=True
                        shift['override_consecutive'] = True
                    elif constraint_type == 'team_balance':
                        # Mark shift as override_team_balance=True
                        shift['override_team_balance'] = True
                    elif constraint_type == 'preference':
                        # Mark shift as override_preference=True
                        shift['override_preference'] = True
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying constraint override: {str(e)}")
            return False
    
    def _apply_manual_resolution(self, conflict: Conflict, resolution: Dict[str, Any]) -> bool:
        """Apply a manual resolution"""
        try:
            changes = resolution['details']['changes']
            
            # Apply each change in the manual resolution
            for change in changes:
                change_type = change.get('type')
                shift_id = change.get('shift_id')
                
                # Find the affected shift
                for shift in conflict.affected_shifts:
                    if shift['id'] == shift_id:
                        if change_type == 'reassign_staff':
                            # Update staff assignment
                            shift['assigned_staff'] = {
                                'id': change['new_staff_id'],
                                'gender': change.get('new_staff_gender', 'F'),
                                'team': change.get('new_staff_team', 'A'),
                                'leave_dates': []
                            }
                        elif change_type == 'modify_shift':
                            # Update shift details
                            if 'new_start_time' in change:
                                shift['start_time'] = change['new_start_time']
                            if 'new_end_time' in change:
                                shift['end_time'] = change['new_end_time']
                            if 'new_type' in change:
                                shift['type'] = change['new_type']
                        elif change_type == 'override_constraint':
                            # Apply constraint override
                            constraint = change.get('constraint')
                            if constraint == 'gender_requirement':
                                shift['gender_requirement'] = None
                            elif constraint == 'consecutive_shifts':
                                shift['override_consecutive'] = True
                            elif constraint == 'team_balance':
                                shift['override_team_balance'] = True
                            elif constraint == 'preference':
                                shift['override_preference'] = True
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying manual resolution: {str(e)}")
            return False

    def _validate_resolution_changes(self, conflict: Conflict, changes: List[Dict[str, Any]]) -> List[str]:
        """Validate proposed resolution changes"""
        errors = []
        
        for change in changes:
            shift_id = change.get('shift_id')
            if not shift_id:
                errors.append("Missing shift_id in change")
                continue
                
            # Validate shift exists
            shift = None
            for s in conflict.affected_shifts:
                if s['id'] == shift_id:
                    shift = s
                    break
            
            if not shift:
                errors.append(f"Shift {shift_id} not found in affected shifts")
                continue
            
            # Validate change type
            change_type = change.get('type')
            if not change_type:
                errors.append(f"Missing change type for shift {shift_id}")
                continue
            
            # Validate change details based on type
            if change_type == 'reassign_staff':
                if 'new_staff_id' not in change:
                    errors.append(f"Missing new_staff_id for reassignment of shift {shift_id}")
            elif change_type == 'modify_shift':
                if not any(k in change for k in ['new_start_time', 'new_end_time', 'new_type']):
                    errors.append(f"No modification specified for shift {shift_id}")
            elif change_type == 'override_constraint':
                if 'constraint' not in change:
                    errors.append(f"Missing constraint type for override on shift {shift_id}")
            else:
                errors.append(f"Invalid change type {change_type} for shift {shift_id}")
        
        return errors
    
    def _get_team_distribution(self, 
                             schedule: Dict[str, Any],
                             start_date: date,
                             end_date: date) -> Dict[str, Any]:
        """Get team distribution metrics"""
        team_stats = defaultdict(lambda: defaultdict(int))
        
        for shift in schedule['shifts']:
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            if start_date <= shift_date <= end_date:
                staff_id = shift['assigned_staff']['id']
                staff = next(s for s in self.staff_loader.load_all_staff() if s.id == staff_id)
                team_stats[staff.team][shift['type']] += 1
                
        return {
            'team_counts': dict(team_stats),
            'balance_score': self._calculate_team_balance_score(team_stats)
        }
    
    def _get_gender_distribution(self, 
                               schedule: Dict[str, Any],
                               start_date: date,
                               end_date: date) -> Dict[str, Any]:
        """Get gender distribution metrics"""
        gender_stats = defaultdict(lambda: defaultdict(int))
        
        for shift in schedule['shifts']:
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            if start_date <= shift_date <= end_date:
                staff_id = shift['assigned_staff']['id']
                staff = next(s for s in self.staff_loader.load_all_staff() if s.id == staff_id)
                gender_stats[staff.gender][shift['type']] += 1
                
        return dict(gender_stats)
    
    def _get_workload_metrics(self, 
                            schedule: Dict[str, Any],
                            start_date: date,
                            end_date: date) -> Dict[str, Any]:
        """Get workload distribution metrics"""
        staff_hours = defaultdict(float)
        
        for shift in schedule['shifts']:
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            if start_date <= shift_date <= end_date:
                staff_id = shift['assigned_staff']['id']
                start_time = datetime.fromisoformat(shift['start_time'])
                end_time = datetime.fromisoformat(shift['end_time'])
                hours = (end_time - start_time).total_seconds() / 3600
                staff_hours[staff_id] += hours
                
        if not staff_hours:
            return {
                'min_hours': 0,
                'max_hours': 0,
                'avg_hours': 0,
                'std_dev': 0
            }
            
        hours_list = list(staff_hours.values())
        avg_hours = sum(hours_list) / len(hours_list)
        variance = sum((h - avg_hours) ** 2 for h in hours_list) / len(hours_list)
        
        return {
            'min_hours': min(hours_list),
            'max_hours': max(hours_list),
            'avg_hours': avg_hours,
            'std_dev': variance ** 0.5,
            'staff_hours': dict(staff_hours)
        }
    
    def _get_preference_satisfaction(self, 
                                   schedule: Dict[str, Any],
                                   start_date: date,
                                   end_date: date) -> Dict[str, Any]:
        """Get preference satisfaction metrics"""
        # TODO: Implement once preference system is added
        return {
            'total_preferences': 0,
            'satisfied_preferences': 0,
            'satisfaction_rate': 1.0
        }
    
    def _would_create_consecutive_violation(self, staff_id: str, new_shift: Dict[str, Any]) -> bool:
        """Check if assigning this shift would create a consecutive shifts violation"""
        new_start = datetime.fromisoformat(new_shift['start_time'])
        new_end = datetime.fromisoformat(new_shift['end_time'])
        
        # Get staff's existing shifts
        staff_shifts = [s for s in new_shift['schedule']['shifts'] 
                       if s['assigned_staff']['id'] == staff_id]
        
        for shift in staff_shifts:
            shift_start = datetime.fromisoformat(shift['start_time'])
            shift_end = datetime.fromisoformat(shift['end_time'])
            
            # Check if shifts are consecutive
            gap = abs((new_start - shift_end).total_seconds() / 3600)
            if gap < 8:  # Less than 8 hours between shifts
                return True
                
        return False
    
    def _would_create_workload_imbalance(self, staff_id: str, new_shift: Dict[str, Any]) -> bool:
        """Check if assigning this shift would create a workload imbalance"""
        # Get current workload metrics
        schedule = new_shift['schedule']
        metrics = self._get_workload_metrics(
            schedule,
            datetime.fromisoformat(new_shift['start_time']).date(),
            datetime.fromisoformat(new_shift['end_time']).date()
        )
        
        # Calculate new hours for this staff member
        new_hours = (datetime.fromisoformat(new_shift['end_time']) - 
                    datetime.fromisoformat(new_shift['start_time'])).total_seconds() / 3600
        
        current_hours = metrics['staff_hours'].get(staff_id, 0)
        new_total = current_hours + new_hours
        
        # Check if this would create too much imbalance
        return new_total > metrics['avg_hours'] * 1.5  # More than 50% above average
    
    def _calculate_team_balance_score(self, team_stats: Dict[str, Dict[str, int]]) -> float:
        """Calculate a score representing team balance (0 = perfect balance)"""
        if not team_stats:
            return 0.0
            
        total_shifts = sum(sum(shifts.values()) for shifts in team_stats.values())
        expected_per_team = total_shifts / len(team_stats)
        
        max_deviation = max(
            abs(sum(shifts.values()) - expected_per_team)
            for shifts in team_stats.values()
        )
        
        return max_deviation / expected_per_team if expected_per_team > 0 else 0.0 

    def _analyze_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Analyze the potential impact of a conflict"""
        impact = {
            'severity': conflict.severity.value,
            'affected_staff_count': len(conflict.affected_staff),
            'affected_shifts_count': len(conflict.affected_shifts),
            'cascade_effects': self._analyze_cascade_effects(conflict),
            'workload_impact': self._analyze_workload_impact(conflict),
            'team_impact': self._analyze_team_impact(conflict),
            'preference_impact': self._analyze_preference_impact(conflict),
            'historical_context': self._get_historical_context(conflict),
            'resolution_complexity': self._calculate_resolution_complexity(conflict)
        }
        return impact
    
    def _analyze_cascade_effects(self, conflict: Conflict) -> Dict[str, Any]:
        """Analyze potential cascade effects of resolving this conflict"""
        cascade_effects = {
            'affected_dates': set(),
            'affected_teams': set(),
            'affected_staff': set(),
            'potential_new_conflicts': []
        }
        
        # Analyze each possible resolution
        for resolution in self.suggest_resolutions(conflict):
            # Create a copy of the schedule to test the resolution
            test_schedule = self._create_test_schedule(conflict)
            
            # Apply the resolution
            if self.apply_resolution(conflict, resolution):
                # Check for new conflicts
                new_conflicts = self.detect_conflicts(test_schedule)
                
                # Record cascade effects
                for new_conflict in new_conflicts:
                    if new_conflict != conflict:
                        cascade_effects['affected_dates'].update(
                            s['date'] for s in new_conflict.affected_shifts
                        )
                        cascade_effects['affected_staff'].update(new_conflict.affected_staff)
                        cascade_effects['potential_new_conflicts'].append({
                            'type': new_conflict.conflict_type.value,
                            'severity': new_conflict.severity.value,
                            'description': new_conflict.description
                        })
                        
                        # Get team information
                        for staff_id in new_conflict.affected_staff:
                            staff = self.staff_loader.get_doctor_by_id(staff_id)
                            if staff:
                                cascade_effects['affected_teams'].add(staff.team)
        
        # Convert sets to lists for JSON serialization
        cascade_effects['affected_dates'] = sorted(cascade_effects['affected_dates'])
        cascade_effects['affected_teams'] = sorted(cascade_effects['affected_teams'])
        cascade_effects['affected_staff'] = sorted(cascade_effects['affected_staff'])
        
        return cascade_effects
    
    def _analyze_workload_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Analyze impact on workload distribution"""
        current_workload = defaultdict(int)
        potential_workload = defaultdict(int)
        
        # Calculate current workload
        for shift in conflict.affected_shifts:
            if shift['assigned_staff']['id']:
                current_workload[shift['assigned_staff']['id']] += 1
        
        # Calculate potential workload after resolutions
        resolutions = self.suggest_resolutions(conflict)
        for resolution in resolutions:
            if resolution['type'] == ConflictResolution.SWAP_STAFF.value:
                staff_id = resolution['details'].get('new_staff_id')
                if staff_id:
                    potential_workload[staff_id] += 1
        
        return {
            'current_workload': dict(current_workload),
            'potential_workload': dict(potential_workload),
            'workload_change': {
                staff_id: potential_workload[staff_id] - current_workload[staff_id]
                for staff_id in set(current_workload) | set(potential_workload)
            }
        }
    
    def _analyze_team_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Analyze impact on team balance"""
        current_team_stats = defaultdict(int)
        potential_team_stats = defaultdict(int)
        
        # Calculate current team distribution
        for shift in conflict.affected_shifts:
            if shift['assigned_staff']['id']:
                staff = self.staff_loader.get_doctor_by_id(shift['assigned_staff']['id'])
                if staff:
                    current_team_stats[staff.team] += 1
        
        # Calculate potential team distribution after resolutions
        resolutions = self.suggest_resolutions(conflict)
        for resolution in resolutions:
            if resolution['type'] in [ConflictResolution.SWAP_STAFF.value, 
                                    ConflictResolution.REASSIGN_SHIFT.value]:
                staff_id = resolution['details'].get('new_staff_id')
                if staff_id:
                    staff = self.staff_loader.get_doctor_by_id(staff_id)
                    if staff:
                        potential_team_stats[staff.team] += 1
        
        return {
            'current_distribution': dict(current_team_stats),
            'potential_distribution': dict(potential_team_stats),
            'team_balance_change': {
                team: potential_team_stats[team] - current_team_stats[team]
                for team in set(current_team_stats) | set(potential_team_stats)
            }
        }
    
    def _analyze_preference_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Analyze impact on staff preferences"""
        current_satisfaction = self._calculate_preference_satisfaction(conflict.affected_shifts)
        potential_satisfaction = {}
        
        # Calculate potential preference satisfaction for each resolution
        resolutions = self.suggest_resolutions(conflict)
        for resolution in resolutions:
            if resolution['type'] in [ConflictResolution.SWAP_STAFF.value, 
                                    ConflictResolution.REASSIGN_SHIFT.value]:
                test_schedule = self._create_test_schedule(conflict)
                if self.apply_resolution(conflict, resolution):
                    satisfaction = self._calculate_preference_satisfaction(
                        test_schedule['shifts']
                    )
                    potential_satisfaction[resolution['type']] = satisfaction
        
        return {
            'current_satisfaction': current_satisfaction,
            'potential_satisfaction': potential_satisfaction,
            'satisfaction_change': {
                res_type: pot_sat - current_satisfaction['overall']
                for res_type, pot_sat in potential_satisfaction.items()
            }
        }
    
    def _calculate_preference_satisfaction(self, shifts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate preference satisfaction metrics for a set of shifts"""
        total_preferences = 0
        satisfied_preferences = 0
        staff_satisfaction = defaultdict(lambda: {'total': 0, 'satisfied': 0})
        
        for shift in shifts:
            if shift['assigned_staff']['id']:
                staff = self.staff_loader.get_doctor_by_id(shift['assigned_staff']['id'])
                if staff and staff.preferences:
                    total_preferences += 1
                    staff_satisfaction[staff.id]['total'] += 1
                    if shift['type'] in staff.preferences:
                        satisfied_preferences += 1
                        staff_satisfaction[staff.id]['satisfied'] += 1
        
        return {
            'overall': satisfied_preferences / total_preferences if total_preferences > 0 else 1.0,
            'by_staff': {
                staff_id: {
                    'satisfaction_rate': stats['satisfied'] / stats['total']
                    if stats['total'] > 0 else 1.0
                }
                for staff_id, stats in staff_satisfaction.items()
            }
        }
    
    def _calculate_resolution_complexity(self, conflict: Conflict) -> Dict[str, Any]:
        """Calculate the complexity of resolving this conflict"""
        resolutions = self.suggest_resolutions(conflict)
        
        return {
            'resolution_count': len(resolutions),
            'cascade_probability': self._estimate_cascade_probability(conflict),
            'constraint_complexity': self._calculate_constraint_complexity(conflict),
            'staff_availability': self._calculate_staff_availability(conflict),
            'timeline_impact': self._calculate_timeline_impact(conflict)
        }
    
    def _estimate_cascade_probability(self, conflict: Conflict) -> float:
        """Estimate the probability of cascade effects"""
        cascade_effects = self._analyze_cascade_effects(conflict)
        
        factors = [
            len(cascade_effects['affected_dates']) / 5,  # Normalize by 5 days
            len(cascade_effects['affected_teams']) / 2,  # Normalize by 2 teams
            len(cascade_effects['affected_staff']) / 4,  # Normalize by 4 staff
            len(cascade_effects['potential_new_conflicts']) / 3  # Normalize by 3 conflicts
        ]
        
        return min(1.0, sum(factors) / len(factors))
    
    def _calculate_constraint_complexity(self, conflict: Conflict) -> float:
        """Calculate the complexity of constraints involved"""
        complexity_weights = {
            ConflictType.GENDER_REQUIREMENT: 0.8,
            ConflictType.CONSECUTIVE_SHIFTS: 0.6,
            ConflictType.TEAM_BALANCE: 0.4,
            ConflictType.STAFF_UNAVAILABLE: 0.9,
            ConflictType.PREFERENCE_VIOLATION: 0.3,
            ConflictType.WORKLOAD_IMBALANCE: 0.5
        }
        
        return complexity_weights.get(conflict.conflict_type, 0.5)
    
    def _calculate_staff_availability(self, conflict: Conflict) -> Dict[str, Any]:
        """Calculate staff availability metrics for resolution"""
        availability = {
            'total_eligible': 0,
            'currently_available': 0,
            'future_available': 0
        }
        
        for shift in conflict.affected_shifts:
            eligible_staff = self._find_eligible_staff(shift)
            availability['total_eligible'] += len(eligible_staff)
            
            # Check current availability
            available_now = [
                staff_id for staff_id in eligible_staff
                if not self._has_conflict(staff_id, shift)
            ]
            availability['currently_available'] += len(available_now)
            
            # Check future availability (next shift)
            next_shift = self._get_next_shift(shift)
            if next_shift:
                future_available = [
                    staff_id for staff_id in eligible_staff
                    if not self._has_conflict(staff_id, next_shift)
                ]
                availability['future_available'] += len(future_available)
        
        # Normalize values
        shift_count = len(conflict.affected_shifts)
        if shift_count > 0:
            availability['total_eligible'] /= shift_count
            availability['currently_available'] /= shift_count
            availability['future_available'] /= shift_count
        
        return availability
    
    def _calculate_timeline_impact(self, conflict: Conflict) -> Dict[str, Any]:
        """Calculate the impact on schedule timeline"""
        affected_dates = set()
        affected_shifts = set()
        future_conflicts = []
        
        # Collect affected dates and shifts
        for shift in conflict.affected_shifts:
            shift_date = datetime.fromisoformat(shift['start_time']).date()
            affected_dates.add(shift_date)
            affected_shifts.add(shift['id'])
        
        # Check for future conflicts
        cascade_effects = self._analyze_cascade_effects(conflict)
        future_conflicts = [
            conflict for conflict in cascade_effects['potential_new_conflicts']
            if any(
                datetime.fromisoformat(shift['start_time']).date() > max(affected_dates)
                for shift in conflict.affected_shifts
            )
        ]
        
        return {
            'date_range': {
                'start': min(affected_dates).isoformat(),
                'end': max(affected_dates).isoformat()
            },
            'affected_days': len(affected_dates),
            'affected_shifts': len(affected_shifts),
            'future_conflicts': len(future_conflicts),
            'resolution_urgency': self._calculate_urgency(min(affected_dates))
        }
    
    def _calculate_urgency(self, earliest_date: date) -> float:
        """Calculate the urgency of resolving the conflict"""
        days_until = (earliest_date - datetime.now().date()).days
        if days_until <= 0:
            return 1.0
        elif days_until <= 7:
            return 0.8
        elif days_until <= 14:
            return 0.5
        else:
            return 0.2
    
    def _has_conflict(self, staff_id: str, shift: Dict[str, Any]) -> bool:
        """Check if staff member has conflicts with a shift"""
        staff = self.staff_loader.get_doctor_by_id(staff_id)
        if not staff:
            return True
            
        shift_date = datetime.fromisoformat(shift['start_time']).date()
        
        # Check leave dates
        if shift_date in staff.leave_dates:
            return True
            
        # Check existing assignments
        for existing_shift in shift['schedule']['shifts']:
            if existing_shift['assigned_staff']['id'] == staff_id:
                existing_date = datetime.fromisoformat(existing_shift['start_time']).date()
                if existing_date == shift_date:
                    return True
        
        return False
    
    def _get_next_shift(self, shift: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the next shift after the given shift"""
        shift_date = datetime.fromisoformat(shift['start_time']).date()
        shift_time = datetime.fromisoformat(shift['start_time']).time()
        
        next_shifts = [
            s for s in shift['schedule']['shifts']
            if datetime.fromisoformat(s['start_time']).date() == shift_date and
            datetime.fromisoformat(s['start_time']).time() > shift_time
        ]
        
        return min(next_shifts, key=lambda s: s['start_time']) if next_shifts else None 