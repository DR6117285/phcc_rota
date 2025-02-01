from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from src.interfaces.staff_interfaces import Doctor
from src.interfaces.shift_interfaces import Shift

@dataclass
class DoctorStats:
    total_shifts: int = 0
    late_shifts: int = 0  # After 17:00
    total_hours: float = 0.0

class IEquityTracker(ABC):
    @abstractmethod
    def record_shift(self, doctor: Doctor, shift: Shift) -> None:
        """Record a shift allocation for equity tracking"""
        pass
    
    @abstractmethod
    def get_doctor_stats(self, doctor_id: str) -> DoctorStats:
        """Get current statistics for a doctor"""
        pass
    
    @abstractmethod
    def get_next_eligible(self, doctors: List[Doctor]) -> Doctor:
        """Get the most eligible doctor from the list based on equity"""
        pass 