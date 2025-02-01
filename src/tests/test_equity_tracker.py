import pytest
from datetime import date, time
from src.interfaces.equity_interfaces import IEquityTracker
from src.interfaces.shift_interfaces import Shift
from src.interfaces.staff_interfaces import Doctor
from src.core.equity_tracker import EquityTracker

def test_equity_tracker_creation():
    tracker = EquityTracker()
    assert isinstance(tracker, IEquityTracker)

def test_record_shift():
    tracker = EquityTracker()
    doctor = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    shift = Shift(
        name="WIC",
        start_time=time(17, 0),
        end_time=time(23, 0),
        gender_requirement="Any",
        day=date(2024, 3, 18)
    )
    
    tracker.record_shift(doctor, shift)
    stats = tracker.get_doctor_stats(doctor.id)
    assert stats.total_shifts == 1
    assert stats.late_shifts == 1
    assert stats.total_hours == 6

def test_get_doctor_stats_nonexistent():
    tracker = EquityTracker()
    stats = tracker.get_doctor_stats("nonexistent")
    assert stats.total_shifts == 0
    assert stats.late_shifts == 0
    assert stats.total_hours == 0

def test_get_next_eligible():
    tracker = EquityTracker()
    doctor1 = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    doctor2 = Doctor(id="M2", name="Kashif Ali Raza", gender="M", team=1)
    
    shift1 = Shift(
        name="WIC",
        start_time=time(17, 0),
        end_time=time(23, 0),
        gender_requirement="Any",
        day=date(2024, 3, 18)
    )
    
    # Record more shifts for doctor1
    tracker.record_shift(doctor1, shift1)
    tracker.record_shift(doctor1, shift1)
    
    # Record fewer shifts for doctor2
    tracker.record_shift(doctor2, shift1)
    
    doctors = [doctor1, doctor2]
    next_doctor = tracker.get_next_eligible(doctors)
    assert next_doctor == doctor2  # Should prefer doctor with fewer shifts 