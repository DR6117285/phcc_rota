from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, time, date
from enum import Enum
from typing import List, Optional, Dict
from src.interfaces.staff_interfaces import Doctor

class ShiftType(str, Enum):
    """Types of shifts available in the system"""
    WBC = "WBC"
    TRIAGE = "TRIAGE"
    ANC = "ANC"
    WIC = "WIC"
    FMC = "FMC"

class GenderRequirement(str, Enum):
    """Gender requirements for shifts"""
    MALE_ONLY = "Male Only"
    FEMALE_ONLY = "Female Only"
    ANY = "Any Gender"

@dataclass
class TimeSlot:
    """Represents a time slot for a shift"""
    start_time: time
    end_time: time
    slots: int = 1  # Number of doctors needed for this time slot

@dataclass
class ShiftDefinition:
    """Defines a shift type with its requirements"""
    shift_type: ShiftType
    time_slot: TimeSlot
    gender_requirement: GenderRequirement
    is_essential: bool = True

@dataclass
class Shift:
    """Represents an actual shift instance on a specific date"""
    id: str
    shift_definition: ShiftDefinition
    date: datetime
    assigned_doctor_id: Optional[str] = None

class IShiftValidator(ABC):
    @abstractmethod
    def validate_shift_matrix(self, shift: Shift) -> bool:
        """Validates shift against availability matrix"""
        pass

    @abstractmethod
    def validate_team_rotation(self, shift: Shift, doctor: Doctor) -> bool:
        """Validates doctor's team matches shift rotation"""
        pass

    @abstractmethod
    def validate_consecutive_shifts(self, doctor: Doctor, current_shift: Shift, allocated_shifts: List[Shift]) -> bool:
        """Checks if doctor can take shift based on their previous allocations"""
        pass

class IShiftAllocator(ABC):
    """Interface for shift allocation logic"""
    
    @abstractmethod
    def allocate_shifts(self, date: datetime) -> List[Shift]:
        """Allocate shifts for a specific date"""
        pass
    
    @abstractmethod
    def get_doctor_shifts(self, doctor_id: str, start_date: datetime, end_date: datetime) -> List[Shift]:
        """Get all shifts allocated to a doctor in a date range"""
        pass
    
    @abstractmethod
    def validate_allocation(self, shift: Shift, doctor_id: str) -> bool:
        """Validate if a doctor can be allocated to a shift"""
        pass

    @abstractmethod
    def validate_gender_requirement(self, shift: Shift, doctor: Doctor) -> bool:
        pass
    
    @abstractmethod
    def get_available_doctors(self, shift: Shift, doctors: List[Doctor]) -> List[Doctor]:
        pass
    
    @abstractmethod
    def allocate_shift(self, shift: Shift, doctors: List[Doctor], allocated_shifts: List[Shift]) -> Doctor:
        pass

class Schedule:
    """Manages a collection of shifts for a period of time"""
    
    def __init__(self):
        self._shifts: List[Shift] = []
        self._shifts_by_date: Dict[date, List[Shift]] = {}
        self._shifts_by_doctor: Dict[str, List[Shift]] = {}
    
    def add_shift(self, shift: Shift) -> None:
        """Add a shift to the schedule"""
        self._shifts.append(shift)
        
        # Index by date
        shift_date = shift.date.date()
        if shift_date not in self._shifts_by_date:
            self._shifts_by_date[shift_date] = []
        self._shifts_by_date[shift_date].append(shift)
        
        # Index by doctor if assigned
        if shift.assigned_doctor_id:
            if shift.assigned_doctor_id not in self._shifts_by_doctor:
                self._shifts_by_doctor[shift.assigned_doctor_id] = []
            self._shifts_by_doctor[shift.assigned_doctor_id].append(shift)
    
    def get_all_shifts(self) -> List[Shift]:
        """Get all shifts in the schedule"""
        return self._shifts.copy()
    
    def get_shifts_by_date(self, target_date: date) -> List[Shift]:
        """Get all shifts for a specific date"""
        return self._shifts_by_date.get(target_date, []).copy()
    
    def get_shifts_by_doctor(self, doctor_id: str) -> List[Shift]:
        """Get all shifts assigned to a specific doctor"""
        return self._shifts_by_doctor.get(doctor_id, []).copy()
    
    def get_shifts_in_range(self, start_date: date, end_date: date) -> List[Shift]:
        """Get all shifts between start_date and end_date inclusive"""
        return [
            shift for shift in self._shifts
            if start_date <= shift.date.date() <= end_date
        ] 