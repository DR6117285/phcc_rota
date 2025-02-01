from datetime import time
from typing import Dict, List
from src.interfaces.equity_interfaces import IEquityTracker, DoctorStats
from src.interfaces.staff_interfaces import Doctor
from src.interfaces.shift_interfaces import Shift

class EquityTracker(IEquityTracker):
    def __init__(self):
        self._stats: Dict[str, DoctorStats] = {}
    
    def record_shift(self, doctor: Doctor, shift: Shift) -> None:
        if doctor.id not in self._stats:
            self._stats[doctor.id] = DoctorStats()
        
        stats = self._stats[doctor.id]
        stats.total_shifts += 1
        
        # Calculate hours worked from shift definition time slot
        time_slot = shift.shift_definition.time_slot
        hours = (time_slot.end_time.hour - time_slot.start_time.hour + 
                (time_slot.end_time.minute - time_slot.start_time.minute) / 60)
        stats.total_hours += hours
        
        # Track late shifts (after 17:00)
        if time_slot.start_time >= time(17, 0):
            stats.late_shifts += 1
    
    def get_doctor_stats(self, doctor_id: str) -> DoctorStats:
        return self._stats.get(doctor_id, DoctorStats())
    
    def get_next_eligible(self, doctors: List[Doctor]) -> Doctor:
        if not doctors:
            raise ValueError("No doctors provided")
            
        # Sort doctors by total shifts (ascending) and total hours (ascending)
        sorted_doctors = sorted(
            doctors,
            key=lambda d: (
                self.get_doctor_stats(d.id).total_shifts,
                self.get_doctor_stats(d.id).total_hours
            )
        )
        
        return sorted_doctors[0] 