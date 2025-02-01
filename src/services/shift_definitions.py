from datetime import time
from typing import List
from src.interfaces.shift_interfaces import (
    ShiftType,
    GenderRequirement,
    TimeSlot,
    ShiftDefinition
)

class ShiftDefinitions:
    """Service providing all shift definitions from requirements"""
    
    @staticmethod
    def get_essential_shifts() -> List[ShiftDefinition]:
        """Get all essential shift definitions that must be filled"""
        return [
            # WBC Shifts
            ShiftDefinition(
                shift_type=ShiftType.WBC,
                time_slot=TimeSlot(start_time=time(7), end_time=time(14)),
                gender_requirement=GenderRequirement.MALE_ONLY,
                is_essential=True
            ),
            ShiftDefinition(
                shift_type=ShiftType.WBC,
                time_slot=TimeSlot(start_time=time(16), end_time=time(22)),
                gender_requirement=GenderRequirement.MALE_ONLY,
                is_essential=True
            ),
            
            # TRIAGE Shifts
            ShiftDefinition(
                shift_type=ShiftType.TRIAGE,
                time_slot=TimeSlot(start_time=time(9), end_time=time(16)),
                gender_requirement=GenderRequirement.MALE_ONLY,
                is_essential=True
            ),
            ShiftDefinition(
                shift_type=ShiftType.TRIAGE,
                time_slot=TimeSlot(start_time=time(14), end_time=time(20), slots=2),
                gender_requirement=GenderRequirement.MALE_ONLY,
                is_essential=True
            ),
            
            # ANC Shifts
            ShiftDefinition(
                shift_type=ShiftType.ANC,
                time_slot=TimeSlot(start_time=time(7), end_time=time(11)),
                gender_requirement=GenderRequirement.FEMALE_ONLY,
                is_essential=True
            ),
            ShiftDefinition(
                shift_type=ShiftType.ANC,
                time_slot=TimeSlot(start_time=time(16), end_time=time(20)),
                gender_requirement=GenderRequirement.FEMALE_ONLY,
                is_essential=True
            ),
            
            # WIC Evening Shifts
            ShiftDefinition(
                shift_type=ShiftType.WIC,
                time_slot=TimeSlot(start_time=time(17), end_time=time(23), slots=2),
                gender_requirement=GenderRequirement.ANY,
                is_essential=True
            ),
            
            # TRIAGE Morning
            ShiftDefinition(
                shift_type=ShiftType.TRIAGE,
                time_slot=TimeSlot(start_time=time(7), end_time=time(14)),
                gender_requirement=GenderRequirement.ANY,
                is_essential=True
            ),
        ]
    
    @staticmethod
    def get_additional_shifts() -> List[ShiftDefinition]:
        """Get additional shift definitions for remaining staff"""
        return [
            # FMC Shifts
            ShiftDefinition(
                shift_type=ShiftType.FMC,
                time_slot=TimeSlot(start_time=time(7), end_time=time(14)),
                gender_requirement=GenderRequirement.ANY,
                is_essential=False
            ),
            ShiftDefinition(
                shift_type=ShiftType.FMC,
                time_slot=TimeSlot(start_time=time(16), end_time=time(22)),
                gender_requirement=GenderRequirement.ANY,
                is_essential=False
            ),
            
            # WIC Regular Shifts
            ShiftDefinition(
                shift_type=ShiftType.WIC,
                time_slot=TimeSlot(start_time=time(7), end_time=time(14)),
                gender_requirement=GenderRequirement.ANY,
                is_essential=False
            ),
            ShiftDefinition(
                shift_type=ShiftType.WIC,
                time_slot=TimeSlot(start_time=time(16), end_time=time(22)),
                gender_requirement=GenderRequirement.ANY,
                is_essential=False
            ),
        ]
    
    @staticmethod
    def get_all_shifts() -> List[ShiftDefinition]:
        """Get all shift definitions"""
        return ShiftDefinitions.get_essential_shifts() + ShiftDefinitions.get_additional_shifts() 