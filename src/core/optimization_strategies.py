from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .optimization_metrics import OptimizationMetrics, OptimizationResult
from ..interfaces.shift_interfaces import Schedule, Shift

class OptimizationStrategy(ABC):
    """Base class for optimization strategies"""
    
    @abstractmethod
    def optimize(self, schedule: Schedule) -> Schedule:
        """Apply optimization strategy to schedule"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name"""
        pass

class PriorityBasedStrategy(OptimizationStrategy):
    """Optimize schedule prioritizing essential shifts"""
    
    def __init__(self, shift_allocator, equity_tracker):
        self.shift_allocator = shift_allocator
        self.equity_tracker = equity_tracker
    
    def get_name(self) -> str:
        return "priority"
    
    def optimize(self, schedule: Schedule) -> Schedule:
        optimized = Schedule()
        all_shifts = schedule.get_all_shifts()
        
        # Sort shifts by priority (essential shifts first)
        shifts_by_priority = sorted(
            all_shifts,
            key=lambda s: (s.shift_definition.is_essential, s.shift_definition.priority),
            reverse=True
        )
        
        # Try to optimize each shift allocation
        for shift in shifts_by_priority:
            if shift.assigned_doctor_id:
                # Get current doctor
                current_doctor = self.shift_allocator.get_doctor_by_id(
                    shift.assigned_doctor_id
                )
                
                # Get all eligible doctors for this shift
                eligible_doctors = self.shift_allocator.get_eligible_doctors(
                    shift,
                    optimized.get_all_shifts()
                )
                
                # Find doctor with best equity score
                best_doctor = self.equity_tracker.get_next_eligible(eligible_doctors)
                
                if best_doctor and best_doctor != current_doctor:
                    optimized_shift = Shift(
                        id=shift.id,
                        shift_definition=shift.shift_definition,
                        date=shift.date,
                        assigned_doctor_id=best_doctor.id
                    )
                    optimized.add_shift(optimized_shift)
                else:
                    optimized.add_shift(shift)
            else:
                # Try to assign unassigned shift
                eligible_doctors = self.shift_allocator.get_eligible_doctors(
                    shift,
                    optimized.get_all_shifts()
                )
                best_doctor = self.equity_tracker.get_next_eligible(eligible_doctors)
                
                if best_doctor:
                    optimized_shift = Shift(
                        id=shift.id,
                        shift_definition=shift.shift_definition,
                        date=shift.date,
                        assigned_doctor_id=best_doctor.id
                    )
                    optimized.add_shift(optimized_shift)
                else:
                    optimized.add_shift(shift)
        
        return optimized

class EquityBasedStrategy(OptimizationStrategy):
    """Optimize schedule focusing on workload equity"""
    
    def __init__(self, shift_allocator, equity_tracker):
        self.shift_allocator = shift_allocator
        self.equity_tracker = equity_tracker
    
    def get_name(self) -> str:
        return "equity"
    
    def optimize(self, schedule: Schedule) -> Schedule:
        optimized = Schedule()
        all_shifts = schedule.get_all_shifts()
        
        # Get current workload stats
        workload_stats = self.equity_tracker.get_workload_stats()
        
        # Sort doctors by workload (least worked first)
        doctors_by_workload = sorted(
            workload_stats.items(),
            key=lambda x: (x[1]['total_hours'], x[1]['total_shifts'])
        )
        
        # Try to assign shifts to underutilized doctors
        for doctor_id, _ in doctors_by_workload:
            doctor = self.shift_allocator.get_doctor_by_id(doctor_id)
            
            # Find eligible shifts for this doctor
            for shift in all_shifts:
                if not shift.assigned_doctor_id:
                    if self.shift_allocator.is_doctor_eligible(doctor, shift):
                        optimized_shift = Shift(
                            id=shift.id,
                            shift_definition=shift.shift_definition,
                            date=shift.date,
                            assigned_doctor_id=doctor.id
                        )
                        optimized.add_shift(optimized_shift)
                        all_shifts.remove(shift)
        
        # Add remaining shifts
        for shift in all_shifts:
            optimized.add_shift(shift)
        
        return optimized

class PreferenceBasedStrategy(OptimizationStrategy):
    """Optimize schedule based on doctor preferences"""
    
    def __init__(self, shift_allocator):
        self.shift_allocator = shift_allocator
    
    def get_name(self) -> str:
        return "preference"
    
    def optimize(self, schedule: Schedule) -> Schedule:
        optimized = Schedule()
        all_shifts = schedule.get_all_shifts()
        
        # Group shifts by type
        shifts_by_type = {}
        for shift in all_shifts:
            shift_type = shift.shift_definition.shift_type
            if shift_type not in shifts_by_type:
                shifts_by_type[shift_type] = []
            shifts_by_type[shift_type].append(shift)
        
        # Try to assign shifts according to preferences
        for shift_type, shifts in shifts_by_type.items():
            for shift in shifts:
                # Find doctors who prefer this shift type
                preferred_doctors = [
                    d for d in self.shift_allocator.staff_loader.load_all_staff()
                    if shift_type in d.preferences
                ]
                
                # Try to assign to a doctor who prefers this shift
                assigned = False
                for doctor in preferred_doctors:
                    if self.shift_allocator.is_doctor_eligible(doctor, shift):
                        optimized_shift = Shift(
                            id=shift.id,
                            shift_definition=shift.shift_definition,
                            date=shift.date,
                            assigned_doctor_id=doctor.id
                        )
                        optimized.add_shift(optimized_shift)
                        assigned = True
                        break
                
                if not assigned:
                    optimized.add_shift(shift)
        
        return optimized

class TeamBalanceStrategy(OptimizationStrategy):
    """Optimize schedule focusing on team balance"""
    
    def __init__(self, shift_allocator):
        self.shift_allocator = shift_allocator
    
    def get_name(self) -> str:
        return "team_balance"
    
    def optimize(self, schedule: Schedule) -> Schedule:
        optimized = Schedule()
        all_shifts = schedule.get_all_shifts()
        
        # Get current team assignments
        team_assignments = {'A': 0, 'B': 0}
        for shift in all_shifts:
            if shift.assigned_doctor_id:
                doctor = self.shift_allocator.get_doctor_by_id(shift.assigned_doctor_id)
                team_assignments[doctor.team] += 1
        
        # Try to balance team assignments
        for shift in all_shifts:
            if shift.assigned_doctor_id:
                current_doctor = self.shift_allocator.get_doctor_by_id(
                    shift.assigned_doctor_id
                )
                current_team = current_doctor.team
                
                # If current team has more assignments, try to swap
                if team_assignments[current_team] > team_assignments['B' if current_team == 'A' else 'A']:
                    # Find eligible doctor from other team
                    other_team_doctors = [
                        d for d in self.shift_allocator.staff_loader.load_all_staff()
                        if d.team != current_team
                    ]
                    
                    for doctor in other_team_doctors:
                        if self.shift_allocator.is_doctor_eligible(doctor, shift):
                            optimized_shift = Shift(
                                id=shift.id,
                                shift_definition=shift.shift_definition,
                                date=shift.date,
                                assigned_doctor_id=doctor.id
                            )
                            optimized.add_shift(optimized_shift)
                            team_assignments[current_team] -= 1
                            team_assignments[doctor.team] += 1
                            break
                    else:
                        optimized.add_shift(shift)
                else:
                    optimized.add_shift(shift)
            else:
                optimized.add_shift(shift)
        
        return optimized

class AggressiveOptimizationStrategy(OptimizationStrategy):
    """Optimize schedule using aggressive optimization techniques"""
    
    def __init__(self, shift_allocator, equity_tracker, shift_validator):
        self.shift_allocator = shift_allocator
        self.equity_tracker = equity_tracker
        self.shift_validator = shift_validator
        self.max_iterations = 100  # Maximum iterations for optimization
        self.improvement_threshold = 0.01  # Minimum improvement to continue
    
    def get_name(self) -> str:
        return "aggressive"
    
    def optimize(self, schedule: Schedule) -> Schedule:
        """Aggressively optimize schedule using multiple techniques"""
        best_schedule = schedule
        best_score = self._evaluate_schedule(schedule)
        iterations_without_improvement = 0
        
        for iteration in range(self.max_iterations):
            # Try different optimization techniques
            candidates = []
            
            # 1. Try swapping shifts between staff members
            candidates.append(self._optimize_by_swapping(best_schedule))
            
            # 2. Try reassigning blocks of shifts
            candidates.append(self._optimize_by_block_reassignment(best_schedule))
            
            # 3. Try balancing workload across teams
            candidates.append(self._optimize_by_team_workload(best_schedule))
            
            # 4. Try optimizing for staff preferences
            candidates.append(self._optimize_by_preferences(best_schedule))
            
            # Evaluate all candidates
            for candidate in candidates:
                score = self._evaluate_schedule(candidate)
                if score > best_score:
                    best_schedule = candidate
                    best_score = score
                    iterations_without_improvement = 0
                    break
            else:
                iterations_without_improvement += 1
            
            # Early stopping if no improvement
            if iterations_without_improvement >= 5:
                break
        
        return best_schedule
    
    def _evaluate_schedule(self, schedule: Schedule) -> float:
        """Evaluate schedule quality with weighted metrics"""
                    metrics = OptimizationMetrics.calculate_from_schedule(
            schedule,
                        self.equity_tracker,
                        self.shift_validator
                    )
        
        # Custom weights for aggressive optimization
        weights = {
            'unassigned': -10.0,  # Heavy penalty for unassigned shifts
            'equity': 3.0,        # High importance for equity
            'team_balance': 2.0,  # Medium importance for team balance
            'preference': 1.5,    # Above average importance for preferences
            'violations': -8.0    # Heavy penalty for violations
        }
        
        return (
            weights['unassigned'] * metrics.unassigned_shifts +
            weights['equity'] * metrics.equity_score +
            weights['team_balance'] * metrics.team_balance_score +
            weights['preference'] * metrics.preference_satisfaction +
            weights['violations'] * metrics.constraint_violations
        )
    
    def _optimize_by_swapping(self, schedule: Schedule) -> Schedule:
        """Optimize by swapping shifts between staff members"""
        optimized = schedule.copy()
        shifts = optimized.get_all_shifts()
        
        for i, shift1 in enumerate(shifts):
            for shift2 in shifts[i+1:]:
                if self._can_swap_shifts(shift1, shift2):
                    # Try swapping
                    staff1_id = shift1.assigned_doctor_id
                    staff2_id = shift2.assigned_doctor_id
                    
                    shift1.assigned_doctor_id = staff2_id
                    shift2.assigned_doctor_id = staff1_id
                    
                    # Revert if not better
                    if not self._is_valid_schedule(optimized):
                        shift1.assigned_doctor_id = staff1_id
                        shift2.assigned_doctor_id = staff2_id
        
        return optimized
    
    def _optimize_by_block_reassignment(self, schedule: Schedule) -> Schedule:
        """Optimize by reassigning blocks of consecutive shifts"""
        optimized = schedule.copy()
        shifts = optimized.get_all_shifts()
        
        # Group shifts into blocks (e.g., morning shifts for a week)
        blocks = self._group_shifts_into_blocks(shifts)
        
        for block in blocks:
            # Find best staff member for this block
            best_staff = None
            best_score = float('-inf')
            
            for staff in self.shift_allocator.staff_loader.load_all_staff():
                # Try assigning all shifts in block to this staff
                original_assignments = [(s, s.assigned_doctor_id) for s in block]
                for shift in block:
                    shift.assigned_doctor_id = staff.id
                
                if self._is_valid_schedule(optimized):
                    score = self._evaluate_schedule(optimized)
                    if score > best_score:
                        best_staff = staff
                        best_score = score
                
                # Restore original assignments
                for shift, original_id in original_assignments:
                    shift.assigned_doctor_id = original_id
            
            # Apply best assignment if found
            if best_staff:
                for shift in block:
                    shift.assigned_doctor_id = best_staff.id
        
        return optimized
    
    def _optimize_by_team_workload(self, schedule: Schedule) -> Schedule:
        """Optimize workload distribution across teams"""
        optimized = schedule.copy()
        shifts = optimized.get_all_shifts()
        
        # Calculate current team workload
        team_workload = {'A': 0, 'B': 0}
        for shift in shifts:
            if shift.assigned_doctor_id:
                staff = self.shift_allocator.get_doctor_by_id(shift.assigned_doctor_id)
                team_workload[staff.team] += 1
        
        # Balance workload by reassigning shifts
        if abs(team_workload['A'] - team_workload['B']) > 2:
            overloaded_team = 'A' if team_workload['A'] > team_workload['B'] else 'B'
            underloaded_team = 'B' if overloaded_team == 'A' else 'A'
            
            for shift in shifts:
                if shift.assigned_doctor_id:
                    staff = self.shift_allocator.get_doctor_by_id(shift.assigned_doctor_id)
                    if staff.team == overloaded_team:
                        # Try to reassign to someone from the underloaded team
                        for other_staff in self.shift_allocator.staff_loader.load_all_staff():
                            if other_staff.team == underloaded_team:
                                original_id = shift.assigned_doctor_id
                                shift.assigned_doctor_id = other_staff.id
                                
                                if self._is_valid_schedule(optimized):
                                    team_workload[overloaded_team] -= 1
                                    team_workload[underloaded_team] += 1
                                    break
                                else:
                                    shift.assigned_doctor_id = original_id
        
        return optimized
    
    def _optimize_by_preferences(self, schedule: Schedule) -> Schedule:
        """Optimize schedule based on staff preferences"""
        optimized = schedule.copy()
        shifts = optimized.get_all_shifts()
        
        for shift in shifts:
            if shift.assigned_doctor_id:
                current_staff = self.shift_allocator.get_doctor_by_id(shift.assigned_doctor_id)
                
                # If current assignment doesn't match preference, try to find someone who prefers it
                if not self._matches_preference(current_staff, shift):
                    for staff in self.shift_allocator.staff_loader.load_all_staff():
                        if self._matches_preference(staff, shift):
                            original_id = shift.assigned_doctor_id
                            shift.assigned_doctor_id = staff.id
                            
                            if not self._is_valid_schedule(optimized):
                                shift.assigned_doctor_id = original_id
            else:
                                break
        
        return optimized
    
    def _can_swap_shifts(self, shift1: Shift, shift2: Shift) -> bool:
        """Check if two shifts can be swapped"""
        if not shift1.assigned_doctor_id or not shift2.assigned_doctor_id:
            return False
            
        staff1 = self.shift_allocator.get_doctor_by_id(shift1.assigned_doctor_id)
        staff2 = self.shift_allocator.get_doctor_by_id(shift2.assigned_doctor_id)
        
        return (
            self.shift_allocator.is_doctor_eligible(staff1, shift2) and
            self.shift_allocator.is_doctor_eligible(staff2, shift1)
        )
    
    def _is_valid_schedule(self, schedule: Schedule) -> bool:
        """Check if schedule is valid"""
        return len(self.shift_validator.validate_schedule(schedule)) == 0
    
    def _group_shifts_into_blocks(self, shifts: List[Shift]) -> List[List[Shift]]:
        """Group shifts into logical blocks (e.g., morning shifts for a week)"""
        blocks = []
        current_block = []
        
        sorted_shifts = sorted(shifts, key=lambda s: (s.date, s.shift_definition.shift_type))
        
        for shift in sorted_shifts:
            if not current_block:
                current_block.append(shift)
            else:
                last_shift = current_block[-1]
                # Check if shifts are part of the same block
                if (shift.date - last_shift.date).days <= 1 and \
                   shift.shift_definition.shift_type == last_shift.shift_definition.shift_type:
                    current_block.append(shift)
                else:
                    if len(current_block) > 1:
                        blocks.append(current_block)
                    current_block = [shift]
        
        if len(current_block) > 1:
            blocks.append(current_block)
        
        return blocks
    
    def _matches_preference(self, staff, shift) -> bool:
        """Check if shift matches staff preference"""
        return shift.shift_definition.shift_type in staff.preferences

class ConflictResolutionStrategy(OptimizationStrategy):
    """Optimize schedule by resolving conflicts"""
    
    def __init__(self, shift_allocator, conflict_resolver):
        self.shift_allocator = shift_allocator
        self.conflict_resolver = conflict_resolver
    
    def get_name(self) -> str:
        return "conflict_resolution"
    
    def optimize(self, schedule: Schedule) -> Schedule:
        optimized = schedule.copy()  # Start with current schedule
        
        # Detect all conflicts
        conflicts = self.conflict_resolver.detect_conflicts(schedule)
        if not conflicts:
            return optimized
        
        # Sort conflicts by severity
        conflicts.sort(key=lambda c: c.severity.value, reverse=True)
        
        # Try to resolve each conflict
        for conflict in conflicts:
            # Get resolution suggestions
            resolutions = self.conflict_resolver.suggest_resolutions(conflict)
            
            # Try each resolution in order
            for resolution in resolutions:
                # Create a temporary schedule to test the resolution
                temp_schedule = optimized.copy()
                
                # Try to apply the resolution
                success = self.conflict_resolver.apply_resolution(
                    conflict,
                    resolution,
                    temp_schedule
                )
                
                if success:
                    # Check if resolution didn't create new conflicts
                    new_conflicts = self.conflict_resolver.detect_conflicts(temp_schedule)
                    if len(new_conflicts) < len(conflicts):
                        optimized = temp_schedule
                        conflicts = new_conflicts
                        break  # Move to next conflict
        
        return optimized 