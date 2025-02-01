import pytest
from src.interfaces.staff_interfaces import Doctor
from src.core.staff_manager import StaffManager

def test_staff_manager_creation():
    manager = StaffManager()
    assert isinstance(manager, StaffManager)

def test_add_doctor():
    manager = StaffManager()
    doctor = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    manager.add_doctor(doctor)
    assert manager.get_doctor("M1") == doctor

def test_get_team_doctors():
    manager = StaffManager()
    doctor1 = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    doctor2 = Doctor(id="F1", name="Eman Hassan Khiri", gender="F", team=1)
    doctor3 = Doctor(id="M10", name="Sahibzada", gender="M", team=2)
    
    manager.add_doctor(doctor1)
    manager.add_doctor(doctor2)
    manager.add_doctor(doctor3)
    
    team1_doctors = manager.get_team_doctors(1)
    assert len(team1_doctors) == 2
    assert doctor1 in team1_doctors
    assert doctor2 in team1_doctors 