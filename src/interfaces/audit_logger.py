from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from src.models.doctor import Doctor
from src.models.shift import Shift
from src.models.doctor_stats import DoctorStats

@dataclass
class ShiftAllocation:
    """Data model for tracking shift allocations with compliance metrics"""
    timestamp: datetime
    doctor: Doctor
    shift: Shift
    gender_compliant: bool
    team_compliant: bool
    equity_stats: DoctorStats

class IAuditLogger(ABC):
    """Interface for audit logging and report generation"""
    
    @abstractmethod
    def log_allocation(self, allocation: ShiftAllocation) -> None:
        """Log a shift allocation with all relevant metrics"""
        pass
    
    @abstractmethod
    def generate_daily_report(self, date: date) -> bytes:
        """Generate Excel report for all allocations on a specific date"""
        pass
    
    @abstractmethod
    def generate_distribution_report(self, start_date: date, end_date: date) -> bytes:
        """Generate Excel report showing shift distribution metrics for a date range"""
        pass 