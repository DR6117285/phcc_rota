import pytest
from datetime import datetime, timedelta
from src.core.rotation_pattern import RotationPattern, RotationShift

@pytest.fixture
def rotation_start():
    """Start date for a rotation cycle (Sunday)"""
    return datetime(2024, 1, 7)  # A Sunday

@pytest.fixture
def rotation_pattern(rotation_start):
    return RotationPattern(rotation_start)

def test_week1_sunday_rotations(rotation_pattern, rotation_start):
    """Test rotations for first Sunday"""
    rotations = rotation_pattern.get_team_rotations(rotation_start)
    assert rotations[1] == RotationShift.AM
    assert rotations[2] == RotationShift.PM

def test_week1_wednesday_rotations(rotation_pattern, rotation_start):
    """Test rotations for first Wednesday"""
    wednesday = rotation_start + timedelta(days=3)
    rotations = rotation_pattern.get_team_rotations(wednesday)
    assert rotations[1] == RotationShift.PM
    assert rotations[2] == RotationShift.AM

def test_week2_monday_rotations(rotation_pattern, rotation_start):
    """Test rotations for second Monday"""
    next_monday = rotation_start + timedelta(days=8)
    rotations = rotation_pattern.get_team_rotations(next_monday)
    assert rotations[1] == RotationShift.PM
    assert rotations[2] == RotationShift.AM

def test_weekend_raises_error(rotation_pattern, rotation_start):
    """Test that weekend dates raise an error"""
    saturday = rotation_start + timedelta(days=6)
    with pytest.raises(ValueError, match="No rotations on weekends"):
        rotation_pattern.get_team_rotations(saturday)

def test_rotation_repeats_after_two_weeks(rotation_pattern, rotation_start):
    """Test that the pattern repeats after two weeks"""
    two_weeks_later = rotation_start + timedelta(days=14)
    original_rotations = rotation_pattern.get_team_rotations(rotation_start)
    repeat_rotations = rotation_pattern.get_team_rotations(two_weeks_later)
    assert original_rotations == repeat_rotations

def test_is_team_on_am(rotation_pattern, rotation_start):
    """Test the is_team_on_am helper method"""
    assert rotation_pattern.is_team_on_am(1, rotation_start) is True
    assert rotation_pattern.is_team_on_am(2, rotation_start) is False

def test_is_team_on_pm(rotation_pattern, rotation_start):
    """Test the is_team_on_pm helper method"""
    assert rotation_pattern.is_team_on_pm(1, rotation_start) is False
    assert rotation_pattern.is_team_on_pm(2, rotation_start) is True 