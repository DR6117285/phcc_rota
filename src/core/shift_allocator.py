from typing import List, Dict, Optional
from datetime import time, timedelta, datetime
from src.interfaces.shift_interfaces import (
    IShiftAllocator,
    IShiftValidator,
    Shift,
    ShiftDefinition,
    GenderRequirement,
    ShiftType
)
from src.interfaces.staff_interfaces import Doctor
from src.interfaces.equity_interfaces import IEquityTracker
from src.core.shift_validator import ShiftValidator
from src.core.rotation_pattern import RotationPattern
from src.services.shift_definitions import ShiftDefinitions
from src.services.data_loader import StaffDataLoader

class ShiftAllocator(IShiftAllocator):
    """Handles allocation of shifts to doctors based on requirements and constraints"""
    
    def __init__(self, validator: ShiftValidator, equity_tracker: IEquityTracker, staff_loader: StaffDataLoader):
        self.validator = validator
        self.equity_tracker = equity_tracker
        self.staff_loader = staff_loader
        self._allocated_shifts: List[Shift] = []
        self._shift_definitions = ShiftDefinitions()
    
    def validate_shift_matrix(self, shift: Shift) -> bool:
        """Validate shift against availability matrix"""
        return self.validator.validate_shift_matrix(shift)
    
    def validate_team_rotation(self, shift: Shift, doctor: Doctor) -> bool:
        """Validate if doctor's team matches shift rotation pattern"""
        return self.validator.validate_team_rotation(shift, doctor)
    
    def validate_consecutive_shifts(self, doctor: Doctor, current_shift: Shift, allocated_shifts: List[Shift]) -> bool:
        """Check if doctor can take shift based on their previous allocations"""
        for shift in allocated_shifts:
            if shift.date.date() == current_shift.date.date() - timedelta(days=1):
                # If previous day was late shift (ending after 22:00)
                if shift.shift_definition.time_slot.end_time >= time(22, 0):
                    # Current shift can't be early (starting before 9:00)
                    if current_shift.shift_definition.time_slot.start_time < time(9, 0):
                        return False
            
            if shift.date.date() == current_shift.date.date():
                return False  # No multiple shifts same day
        
        return True
    
    def validate_gender_requirement(self, shift: Shift, doctor: Doctor) -> bool:
        """Validate if a doctor meets the gender requirement for a shift"""
        return self.validator.validate_gender_requirement(shift, doctor)
    
    def get_available_doctors(self, shift: Shift, doctors: List[Doctor]) -> List[Doctor]:
        """Get list of doctors available for a shift"""
        return [
            doctor for doctor in doctors
            if self.validate_allocation(shift, doctor.id)
        ]
    
    def allocate_shift(self, shift: Shift, doctors: List[Doctor], allocated_shifts: List[Shift]) -> Optional[Doctor]:
        """Allocate a specific shift to an available doctor"""
        self._allocated_shifts.extend(allocated_shifts)
        return self._allocate_shift_to_doctor(shift, doctors)
    
    def allocate_shifts(self, date: datetime) -> List[Shift]:
        """Allocate shifts for a specific date"""
        # Get all shift definitions for the day
        essential_shifts = self._create_shifts(
            self._shift_definitions.get_essential_shifts(),
            date
        )
        additional_shifts = self._create_shifts(
            self._shift_definitions.get_additional_shifts(),
            date
        )
        
        # First allocate essential shifts
        allocated_essential = self._allocate_shift_batch(essential_shifts)
        
        # Then allocate additional shifts with remaining doctors
        allocated_additional = self._allocate_shift_batch(additional_shifts)
        
        return allocated_essential + allocated_additional
    
    def _create_shifts(self, definitions: List[ShiftDefinition], date: datetime) -> List[Shift]:
        """Create shift instances from definitions for a specific date"""
        shifts = []
        for definition in definitions:
            # Create multiple shifts if more than one slot is needed
            for slot in range(definition.time_slot.slots):
                shift_id = f"{definition.shift_type.value}_{date.strftime('%Y%m%d')}_{slot+1}"
                shifts.append(Shift(
                    id=shift_id,
                    shift_definition=definition,
                    date=date,
                    assigned_doctor_id=None
                ))
        return shifts
    
    def _allocate_shift_batch(self, shifts: List[Shift]) -> List[Shift]:
        """Allocate a batch of shifts"""
        allocated = []
        
        # Sort shifts by priority (TRIAGE first, then other essential shifts)
        sorted_shifts = sorted(shifts, key=self._get_shift_priority, reverse=True)
        
        for shift in sorted_shifts:
            if not self.validator.validate_shift_matrix(shift):
                continue
            
            # Special handling for TRIAGE 2-8 shifts (need one from each team)
            if (shift.shift_definition.shift_type == ShiftType.TRIAGE and
                shift.shift_definition.time_slot.start_time.hour == 14):
                self._allocate_balanced_triage_shift(shift)
                if shift.assigned_doctor_id:
                    allocated.append(shift)
                continue
            
            # Try to allocate the shift
            doctor = self._allocate_shift_to_doctor(shift)
            if doctor:
                allocated.append(shift)
                self._allocated_shifts.append(shift)
        
        return allocated
    
    def _get_shift_priority(self, shift: Shift) -> int:
        """Get priority score for shift allocation order"""
        if (shift.shift_definition.shift_type == ShiftType.TRIAGE and
            shift.shift_definition.time_slot.start_time.hour == 14):
            return 100  # Highest priority for TRIAGE 2-8
        elif shift.shift_definition.is_essential:
            return 50   # Essential shifts
        return 0        # Additional shifts
    
    def _allocate_balanced_triage_shift(self, shift: Shift) -> None:
        """Allocate TRIAGE 2-8 shift ensuring team balance"""
        team1_doctors = self.staff_loader.load_team_1()
        team2_doctors = self.staff_loader.load_team_2()
        
        # Check current allocations for this shift type on this day
        existing_allocations = [
            s for s in self._allocated_shifts
            if (s.shift_definition.shift_type == ShiftType.TRIAGE and
                s.shift_definition.time_slot.start_time.hour == 14 and
                s.date.date() == shift.date.date())
        ]
        
        if not existing_allocations:
            # First allocation - try team 1 first
            available = self.get_available_doctors(shift, team1_doctors)
            if available:
                self._allocate_shift_to_doctor(shift, available)
        else:
            # Second allocation - must be from other team
            existing_doctor = self._get_doctor_by_id(existing_allocations[0].assigned_doctor_id)
            if existing_doctor:
                other_team = team2_doctors if existing_doctor.team == 1 else team1_doctors
                available = self.get_available_doctors(shift, other_team)
                if available:
                    self._allocate_shift_to_doctor(shift, available)
    
    def _allocate_shift_to_doctor(self, shift: Shift, doctors: Optional[List[Doctor]] = None) -> Optional[Doctor]:
        """Allocate shift to most eligible doctor"""
        if doctors is None:
            doctors = self.staff_loader.load_all_staff()
            
        available_doctors = self.get_available_doctors(shift, doctors)
        if not available_doctors:
            return None
            
        # Use equity tracker to select most eligible doctor
        selected_doctor = self.equity_tracker.get_next_eligible(available_doctors)
        shift.assigned_doctor_id = selected_doctor.id
        self.equity_tracker.record_shift(selected_doctor, shift)
        
        return selected_doctor
    
    def _get_doctor_by_id(self, doctor_id: str) -> Optional[Doctor]:
        """Get doctor by ID from staff loader"""
        all_doctors = self.staff_loader.load_all_staff()
        return next((d for d in all_doctors if d.id == doctor_id), None)
    
    def get_doctor_shifts(self, doctor_id: str, start_date: datetime, end_date: datetime) -> List[Shift]:
        """Get all shifts allocated to a doctor in a date range"""
        return [
            shift for shift in self._allocated_shifts
            if (shift.assigned_doctor_id == doctor_id and
                start_date <= shift.date <= end_date)
        ]
    
    def validate_allocation(self, shift: Shift, doctor_id: str) -> bool:
        """Validate if a doctor can be allocated to a shift"""
        doctor = self._get_doctor_by_id(doctor_id)
        if not doctor:
            return False
            
        return all([
            self.validate_shift_matrix(shift),
            self.validate_gender_requirement(shift, doctor),
            self.validate_team_rotation(shift, doctor),
            self.validate_consecutive_shifts(doctor, shift, self._allocated_shifts)
        ]) 