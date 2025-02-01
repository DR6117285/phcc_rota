from datetime import datetime, time, timedelta
from typing import List, Dict
from src.interfaces.shift_interfaces import IShiftValidator, Shift, GenderRequirement, ShiftType
from src.interfaces.staff_interfaces import Doctor
from src.core.rotation_pattern import RotationPattern, RotationShift

class ShiftValidator(IShiftValidator):
    """Validates shift allocations against various constraints"""
    
    def __init__(self, rotation_pattern: RotationPattern):
        self.rotation_pattern = rotation_pattern
        self._shift_matrix = self._initialize_shift_matrix()
    
    def _initialize_shift_matrix(self) -> Dict[str, Dict[int, bool]]:
        """Initialize the shift availability matrix from requirements"""
        # Days: 0=Sunday, 4=Thursday
        matrix = {
            "WBC_AM": {0: False, 1: True, 2: True, 3: True, 4: False},
            "WBC_PM": {0: False, 1: True, 2: True, 3: False, 4: False},
            "TRIAGE_9_4": {0: True, 1: True, 2: True, 3: True, 4: True},
            "TRIAGE_2_8": {0: True, 1: True, 2: True, 3: True, 4: True},
            "ANC_AM": {0: True, 1: True, 2: True, 3: True, 4: False},
            "ANC_PM": {0: True, 1: True, 2: True, 3: True, 4: False},
            "FMC_AM": {0: True, 1: True, 2: True, 3: True, 4: True},
            "FMC_PM": {0: True, 1: True, 2: True, 3: True, 4: True},
            "WIC_AM": {0: True, 1: True, 2: True, 3: True, 4: True},
            "WIC_PM": {0: True, 1: True, 2: True, 3: True, 4: True},
            "WIC_5_11": {0: True, 1: True, 2: True, 3: True, 4: True},
            "TRIAGE_7_2": {0: True, 1: True, 2: True, 3: True, 4: True},
        }
        return matrix
    
    def validate_shift_matrix(self, shift: Shift) -> bool:
        """Validates shift against availability matrix"""
        day_of_week = shift.date.weekday()
        if day_of_week > 4:  # Weekend
            return False
            
        shift_key = self._get_matrix_key(shift)
        return self._shift_matrix[shift_key][day_of_week]
    
    def _get_matrix_key(self, shift: Shift) -> str:
        """Convert shift to matrix key"""
        shift_type = shift.shift_definition.shift_type.value
        start_time = shift.shift_definition.time_slot.start_time
        
        if start_time == time(7):
            return f"{shift_type}_AM"
        elif start_time == time(16):
            return f"{shift_type}_PM"
        elif start_time == time(17):
            return f"{shift_type}_5_11"
        elif start_time == time(9):
            return f"{shift_type}_9_4"
        elif start_time == time(14):
            return f"{shift_type}_2_8"
        else:
            return f"{shift_type}_7_2"
    
    def validate_team_rotation(self, shift: Shift, doctor: Doctor) -> bool:
        """Validates doctor's team matches shift rotation"""
        shift_time = shift.shift_definition.time_slot.start_time
        
        # Get doctor's team rotation for the day
        is_am_rotation = self.rotation_pattern.is_team_on_am(doctor.team, shift.date)
        
        # Special case: 2pm-8pm shifts require one doctor from each team
        if (shift.shift_definition.shift_type == ShiftType.TRIAGE and 
            shift_time == time(14)):
            # TODO: Need to check current allocations to ensure balance
            return True
            
        # AM shifts (7am-2pm) should be taken by AM rotation team
        if shift_time.hour < 12:
            return is_am_rotation
        # PM shifts (2pm onwards) should be taken by PM rotation team
        else:
            return not is_am_rotation
    
    def validate_consecutive_shifts(self, doctor: Doctor, current_shift: Shift, allocated_shifts: List[Shift]) -> bool:
        """Checks if doctor can take shift based on their previous allocations"""
        current_date = current_shift.date.date()
        current_start = current_shift.shift_definition.time_slot.start_time
        current_end = current_shift.shift_definition.time_slot.end_time
        
        for shift in allocated_shifts:
            if shift.assigned_doctor_id != doctor.id:
                continue
                
            shift_date = shift.date.date()
            shift_start = shift.shift_definition.time_slot.start_time
            shift_end = shift.shift_definition.time_slot.end_time
            
            # Same day checks
            if shift_date == current_date:
                return False  # No multiple shifts per day
            
            # Previous day checks
            if shift_date == current_date - timedelta(days=1):
                # No late shift (ending after 22:00) followed by early shift (before 9:00)
                if shift_end >= time(22) and current_start < time(9):
                    return False
                    
                # Special case: Tuesday 5pm-11pm should be followed by Wednesday 2pm-8pm or 9am-4pm
                if (shift_date.weekday() == 1 and  # Tuesday
                    shift_start == time(17) and shift_end == time(23)):  # 5pm-11pm
                    if current_date.weekday() == 2:  # Wednesday
                        valid_next_shifts = [
                            (time(14), time(20)),  # 2pm-8pm
                            (time(9), time(16))    # 9am-4pm
                        ]
                        return (current_start, current_end) in valid_next_shifts
            
            # Maximum one 2pm-8pm shift per 5-day AM/PM run
            if (shift_start == time(14) and shift_end == time(20) and
                current_start == time(14) and current_end == time(20)):
                days_between = abs((current_date - shift_date).days)
                if days_between <= 5:
                    return False
        
        return True
    
    def validate_gender_requirement(self, shift: Shift, doctor: Doctor) -> bool:
        """Validates if doctor meets the gender requirement for the shift"""
        requirement = shift.shift_definition.gender_requirement
        
        if requirement == GenderRequirement.ANY:
            return True
        elif requirement == GenderRequirement.MALE_ONLY:
            return doctor.gender == "M"
        elif requirement == GenderRequirement.FEMALE_ONLY:
            return doctor.gender == "F"
        
        return False  # Unknown requirement 