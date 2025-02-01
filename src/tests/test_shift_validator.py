import pytest
from datetime import datetime, time
from src.core.shift_validator import ShiftValidator
from src.core.rotation_pattern import RotationPattern
from src.interfaces.shift_interfaces import (
    Shift,
    ShiftDefinition,
    ShiftType,
    GenderRequirement,
    TimeSlot
)
from src.interfaces.staff_interfaces import Doctor

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
def male_doctor():
    return Doctor(id="M1", name="Dr. Smith", gender="M", team=1)

@pytest.fixture
def female_doctor():
    return Doctor(id="F1", name="Dr. Jones", gender="F", team=2)

@pytest.fixture
def wbc_morning_shift(rotation_start):
    definition = ShiftDefinition(
        shift_type=ShiftType.WBC,
        time_slot=TimeSlot(start_time=time(7), end_time=time(14)),
        gender_requirement=GenderRequirement.MALE_ONLY
    )
    return Shift(
        id="WBC_20240107_1",
        shift_definition=definition,
        date=rotation_start
    )

def test_validate_gender_requirement_male_only(validator, male_doctor, female_doctor, wbc_morning_shift):
    """Test gender validation for male-only shift"""
    assert validator.validate_gender_requirement(wbc_morning_shift, male_doctor) is True
    assert validator.validate_gender_requirement(wbc_morning_shift, female_doctor) is False

def test_validate_gender_requirement_any_gender(validator, male_doctor, female_doctor, wbc_morning_shift):
    """Test gender validation for any-gender shift"""
    wbc_morning_shift.shift_definition.gender_requirement = GenderRequirement.ANY
    assert validator.validate_gender_requirement(wbc_morning_shift, male_doctor) is True
    assert validator.validate_gender_requirement(wbc_morning_shift, female_doctor) is True

def test_validate_shift_matrix_wbc_sunday(validator, wbc_morning_shift):
    """Test shift matrix validation for WBC on Sunday"""
    assert validator.validate_shift_matrix(wbc_morning_shift) is False

def test_validate_shift_matrix_wbc_monday(validator, wbc_morning_shift):
    """Test shift matrix validation for WBC on Monday"""
    wbc_morning_shift.date = datetime(2024, 1, 8)  # Monday
    assert validator.validate_shift_matrix(wbc_morning_shift) is True

def test_validate_team_rotation_am_shift(validator, male_doctor, wbc_morning_shift):
    """Test team rotation validation for AM shift"""
    # Team 1 is on AM rotation on Sunday
    assert validator.validate_team_rotation(wbc_morning_shift, male_doctor) is True
    
    # Change to team 2 (should be PM rotation)
    male_doctor.team = 2
    assert validator.validate_team_rotation(wbc_morning_shift, male_doctor) is False

def test_validate_consecutive_shifts(validator, male_doctor, wbc_morning_shift):
    """Test consecutive shifts validation"""
    # First shift should be valid
    assert validator.validate_consecutive_shifts(male_doctor, wbc_morning_shift, []) is True
    
    # Same day shift should be invalid
    allocated = [wbc_morning_shift]
    assert validator.validate_consecutive_shifts(male_doctor, wbc_morning_shift, allocated) is False 