import pytest
from datetime import datetime, time, date
from src.interfaces.shift_interfaces import IShiftAllocator, Shift
from src.interfaces.staff_interfaces import Doctor
from src.core.shift_allocator import ShiftAllocator
from src.core.equity_tracker import EquityTracker
from src.core.shift_validator import ShiftValidator
from src.core.rotation_pattern import RotationPattern
from src.interfaces.shift_interfaces import (
    ShiftDefinition,
    ShiftType,
    GenderRequirement,
    TimeSlot
)
from src.services.data_loader import StaffDataLoader

@pytest.fixture
def rotation_start():
    return datetime(2024, 1, 7)  # A Sunday

@pytest.fixture
def rotation_pattern(rotation_start):
    return RotationPattern(rotation_start)

@pytest.fixture
def validator(rotation_pattern):
    return ShiftValidator(rotation_pattern)

@pytest.fixture
def equity_tracker():
    return EquityTracker()

@pytest.fixture
def staff_loader():
    return StaffDataLoader()

@pytest.fixture
def allocator(validator, equity_tracker, staff_loader):
    return ShiftAllocator(validator, equity_tracker, staff_loader)

@pytest.fixture
def doctors():
    return StaffDataLoader.load_all_staff()

@pytest.fixture
def test_shift(rotation_start):
    """Create a test shift for Monday morning WBC"""
    definition = ShiftDefinition(
        shift_type=ShiftType.WBC,
        time_slot=TimeSlot(start_time=time(7), end_time=time(14)),
        gender_requirement=GenderRequirement.MALE_ONLY
    )
    return Shift(
        id="WBC_20240108_1",  # Monday
        shift_definition=definition,
        date=datetime(2024, 1, 8)  # Monday
    )

def test_shift_allocator_creation(allocator):
    assert isinstance(allocator, IShiftAllocator)

def test_validate_gender_requirement():
    allocator = ShiftAllocator()
    male_doctor = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    female_doctor = Doctor(id="F1", name="Eman Hassan Khiri", gender="F", team=1)
    
    male_shift = Shift(
        name="WBC",
        start_time=time(7, 0),
        end_time=time(14, 0),
        gender_requirement="M"
    )
    
    any_shift = Shift(
        name="WIC",
        start_time=time(17, 0),
        end_time=time(23, 0),
        gender_requirement="Any"
    )
    
    assert allocator.validate_gender_requirement(male_shift, male_doctor) == True
    assert allocator.validate_gender_requirement(male_shift, female_doctor) == False
    assert allocator.validate_gender_requirement(any_shift, male_doctor) == True
    assert allocator.validate_gender_requirement(any_shift, female_doctor) == True

def test_get_available_doctors():
    allocator = ShiftAllocator()
    doctor1 = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    doctor2 = Doctor(id="F1", name="Eman Hassan Khiri", gender="F", team=1)
    
    shift = Shift(
        name="WBC",
        start_time=time(7, 0),
        end_time=time(14, 0),
        gender_requirement="M"
    )
    
    doctors = [doctor1, doctor2]
    available = allocator.get_available_doctors(shift, doctors)
    assert len(available) == 1
    assert available[0] == doctor1 

def test_validate_shift_matrix():
    allocator = ShiftAllocator()
    
    # WBC shift on Thursday (not available per matrix)
    invalid_shift = Shift(
        name="WBC",
        start_time=time(7, 0),
        end_time=time(14, 0),
        gender_requirement="M",
        day=date(2024, 3, 21),  # A Thursday
    )
    
    # WBC shift on Monday (available per matrix)
    valid_shift = Shift(
        name="WBC",
        start_time=time(7, 0),
        end_time=time(14, 0),
        gender_requirement="M",
        day=date(2024, 3, 18),  # A Monday
    )
    
    assert allocator.validate_shift_matrix(invalid_shift) == False
    assert allocator.validate_shift_matrix(valid_shift) == True

def test_validate_team_rotation():
    allocator = ShiftAllocator()
    doctor = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    
    # Team 1 AM shift when they should be PM
    invalid_shift = Shift(
        name="WBC",
        start_time=time(7, 0),
        end_time=time(14, 0),
        gender_requirement="M",
        day=date(2024, 3, 20),  # Wednesday Week 1
        team_requirement=1
    )
    
    # Team 1 AM shift when they should be AM
    valid_shift = Shift(
        name="WBC",
        start_time=time(7, 0),
        end_time=time(14, 0),
        gender_requirement="M",
        day=date(2024, 3, 18),  # Monday Week 1
        team_requirement=1
    )
    
    assert allocator.validate_team_rotation(invalid_shift, doctor) == False
    assert allocator.validate_team_rotation(valid_shift, doctor) == True

def test_validate_consecutive_shifts():
    allocator = ShiftAllocator()
    doctor = Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1)
    
    # Previous late shift
    previous_shift = Shift(
        name="WIC",
        start_time=time(17, 0),
        end_time=time(23, 0),
        gender_requirement="Any",
        day=date(2024, 3, 18)
    )
    
    # Early shift next day
    early_shift = Shift(
        name="WBC",
        start_time=time(7, 0),
        end_time=time(14, 0),
        gender_requirement="M",
        day=date(2024, 3, 19)
    )
    
    allocated_shifts = [previous_shift]
    
    assert allocator.validate_consecutive_shifts(doctor, early_shift, allocated_shifts) == False 

def test_allocate_shifts_for_day(allocator, rotation_start):
    """Test allocating all shifts for a day"""
    shifts = allocator.allocate_shifts(datetime(2024, 1, 8))  # Monday
    assert len(shifts) > 0
    
    # Check essential shifts are allocated first
    essential_shifts = [s for s in shifts if s.shift_definition.is_essential]
    assert len(essential_shifts) > 0
    
    # Verify no weekend allocations
    weekend_shifts = allocator.allocate_shifts(datetime(2024, 1, 13))  # Saturday
    assert len(weekend_shifts) == 0

def test_validate_gender_requirement(allocator, test_shift, doctors):
    """Test gender requirement validation"""
    male_doctor = next(d for d in doctors if d.gender == "M")
    female_doctor = next(d for d in doctors if d.gender == "F")
    
    assert allocator.validate_gender_requirement(test_shift, male_doctor) is True
    assert allocator.validate_gender_requirement(test_shift, female_doctor) is False

def test_get_available_doctors(allocator, test_shift, doctors):
    """Test getting available doctors for a shift"""
    available = allocator.get_available_doctors(test_shift, doctors)
    
    # Should only get male doctors from team 1 (AM rotation on Monday)
    assert all(d.gender == "M" for d in available)
    assert all(d.team == 1 for d in available)

def test_allocate_shift(allocator, test_shift, doctors):
    """Test allocating a specific shift"""
    doctor = allocator.allocate_shift(test_shift, doctors, [])
    assert doctor is not None
    assert doctor.gender == "M"  # Should be male for WBC
    assert doctor.team == 1  # Should be team 1 for Monday morning
    assert test_shift.assigned_doctor_id == doctor.id

def test_get_doctor_shifts(allocator, test_shift, doctors):
    """Test retrieving a doctor's shifts"""
    doctor = allocator.allocate_shift(test_shift, doctors, [])
    
    shifts = allocator.get_doctor_shifts(
        doctor.id,
        datetime(2024, 1, 1),
        datetime(2024, 1, 31)
    )
    
    assert len(shifts) == 1
    assert shifts[0].id == test_shift.id

def test_no_double_booking(allocator, doctors):
    """Test that a doctor cannot be allocated two shifts on the same day"""
    # Create two shifts for the same day
    morning_shift = ShiftDefinition(
        shift_type=ShiftType.WBC,
        time_slot=TimeSlot(start_time=time(7), end_time=time(14)),
        gender_requirement=GenderRequirement.MALE_ONLY
    )
    afternoon_shift = ShiftDefinition(
        shift_type=ShiftType.TRIAGE,
        time_slot=TimeSlot(start_time=time(14), end_time=time(20)),
        gender_requirement=GenderRequirement.MALE_ONLY
    )
    
    date = datetime(2024, 1, 8)  # Monday
    shift1 = Shift(id="WBC_20240108_1", shift_definition=morning_shift, date=date)
    shift2 = Shift(id="TRIAGE_20240108_1", shift_definition=afternoon_shift, date=date)
    
    # Allocate first shift
    doctor1 = allocator.allocate_shift(shift1, doctors, [])
    assert doctor1 is not None
    
    # Try to allocate second shift to same doctor
    available = allocator.get_available_doctors(shift2, [doctor1])
    assert len(available) == 0  # Doctor should not be available for second shift 

def test_triage_2_8_team_balance(allocator):
    """Test that TRIAGE 2-8 shifts are balanced between teams"""
    monday = datetime(2024, 1, 8)
    shifts = allocator.allocate_shifts(monday)
    
    # Find TRIAGE 2-8 shifts
    triage_shifts = [
        s for s in shifts
        if (s.shift_definition.shift_type == ShiftType.TRIAGE and
            s.shift_definition.time_slot.start_time == time(14))
    ]
    
    assert len(triage_shifts) == 2  # Should have two slots filled
    
    # Get doctors for each shift
    doctors = [
        allocator._get_doctor_by_id(shift.assigned_doctor_id)
        for shift in triage_shifts
    ]
    
    # Verify one from each team
    teams = [d.team for d in doctors if d]
    assert 1 in teams and 2 in teams

def test_consecutive_shift_rules(allocator):
    """Test consecutive shift allocation rules"""
    # Allocate Tuesday 5pm-11pm shift
    tuesday = datetime(2024, 1, 9)
    tuesday_shifts = allocator.allocate_shifts(tuesday)
    late_shifts = [
        s for s in tuesday_shifts
        if (s.shift_definition.shift_type == ShiftType.WIC and
            s.shift_definition.time_slot.start_time == time(17))
    ]
    assert len(late_shifts) > 0
    
    # Get doctor who got the late shift
    late_shift_doctor_id = late_shifts[0].assigned_doctor_id
    
    # Allocate Wednesday shifts
    wednesday = datetime(2024, 1, 10)
    wednesday_shifts = allocator.allocate_shifts(wednesday)
    
    # Check that doctor got appropriate next shift
    doctor_wednesday_shifts = [
        s for s in wednesday_shifts
        if s.assigned_doctor_id == late_shift_doctor_id
    ]
    
    if doctor_wednesday_shifts:
        shift = doctor_wednesday_shifts[0]
        start_time = shift.shift_definition.time_slot.start_time
        assert start_time in [time(9), time(14)]  # Should be 9am-4pm or 2pm-8pm

def test_equity_based_allocation(allocator, test_shift):
    """Test that allocation considers equity metrics"""
    # Allocate same shift type multiple times
    shifts = []
    dates = [
        datetime(2024, 1, 8),
        datetime(2024, 1, 9),
        datetime(2024, 1, 10)
    ]
    
    for date in dates:
        shift = Shift(
            id=f"WBC_{date.strftime('%Y%m%d')}_1",
            shift_definition=test_shift.shift_definition,
            date=date
        )
        doctor = allocator.allocate_shift(shift, allocator.staff_loader.load_team_1(), shifts)
        assert doctor is not None
        shifts.append(shift)
    
    # Verify different doctors were chosen
    doctor_ids = [s.assigned_doctor_id for s in shifts]
    assert len(set(doctor_ids)) > 1  # Should use different doctors

def test_gender_requirement_compliance(allocator):
    """Test that gender requirements are strictly followed"""
    monday = datetime(2024, 1, 8)
    shifts = allocator.allocate_shifts(monday)
    
    for shift in shifts:
        if shift.assigned_doctor_id:
            doctor = allocator._get_doctor_by_id(shift.assigned_doctor_id)
            assert allocator.validate_gender_requirement(shift, doctor)

def test_team_rotation_compliance(allocator):
    """Test that team rotation pattern is followed"""
    monday = datetime(2024, 1, 8)
    shifts = allocator.allocate_shifts(monday)
    
    for shift in shifts:
        if shift.assigned_doctor_id and shift.shift_definition.time_slot.start_time != time(14):
            doctor = allocator._get_doctor_by_id(shift.assigned_doctor_id)
            assert allocator.validator.validate_team_rotation(shift, doctor) 