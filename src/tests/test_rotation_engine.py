import pytest
from datetime import datetime, timedelta, date, time
from src.core.rotation_engine import RotationEngine
from src.core.shift_allocator import ShiftAllocator
from src.core.shift_validator import ShiftValidator
from src.core.rotation_pattern import RotationPattern
from src.core.equity_tracker import EquityTracker
from src.interfaces.shift_interfaces import Schedule, Shift
from src.services.data_loader import StaffDataLoader
from src.strategies.aggressive_optimization_strategy import AggressiveOptimizationStrategy
from src.metrics.optimization_metrics import OptimizationMetrics
from unittest.mock import Mock
from typing import List, Optional

@pytest.fixture
def rotation_start():
    """Start date for rotation (Sunday)"""
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
def shift_allocator(validator, equity_tracker, staff_loader):
    return ShiftAllocator(validator, equity_tracker, staff_loader)

@pytest.fixture
def rotation_engine(shift_allocator, rotation_pattern):
    return RotationEngine(shift_allocator, rotation_pattern)

def test_generate_schedule_basic(rotation_engine, rotation_start):
    """Test basic schedule generation for a single day"""
    schedule = rotation_engine.generate_schedule(
        start_date=rotation_start,
        end_date=rotation_start
    )
    
    assert isinstance(schedule, Schedule)
    assert len(schedule.get_all_shifts()) > 0

def test_generate_schedule_week(rotation_engine, rotation_start):
    """Test schedule generation for a week"""
    end_date = rotation_start + timedelta(days=6)
    schedule = rotation_engine.generate_schedule(
        start_date=rotation_start,
        end_date=end_date
    )
    
    # Should have shifts for each weekday (5 days, ~3 shifts per day)
    shifts = schedule.get_all_shifts()
    assert len(shifts) == 15  # 3 shifts * 5 weekdays

def test_optimize_schedule(rotation_engine, rotation_start):
    """Test schedule optimization"""
    schedule = rotation_engine.generate_schedule(
        start_date=rotation_start,
        end_date=rotation_start
    )
    
    optimized = rotation_engine.optimize_schedule(schedule)
    assert isinstance(optimized, Schedule)
    
    # Optimization should not remove shifts
    assert len(optimized.get_all_shifts()) == len(schedule.get_all_shifts())

def test_no_weekend_shifts(rotation_engine, rotation_start):
    """Test that no shifts are generated for weekends"""
    saturday = rotation_start + timedelta(days=6)
    sunday = rotation_start + timedelta(days=7)
    
    schedule = rotation_engine.generate_schedule(
        start_date=saturday,
        end_date=sunday
    )
    
    assert len(schedule.get_all_shifts()) == 0

def test_pattern_compliance(rotation_engine, rotation_start):
    """Test that generated schedule follows rotation pattern"""
    monday = rotation_start + timedelta(days=1)
    schedule = rotation_engine.generate_schedule(
        start_date=monday,
        end_date=monday
    )
    
    shifts = schedule.get_all_shifts()
    for shift in shifts:
        if shift.assigned_doctor_id:
            doctor = rotation_engine.shift_allocator._get_doctor_by_id(
                shift.assigned_doctor_id
            )
            assert rotation_engine.pattern.is_team_on_correct_rotation(
                doctor.team,
                shift.date,
                shift.shift_definition.time_slot
            )

def test_constraint_satisfaction(rotation_engine, rotation_start):
    """Test that generated schedule satisfies all constraints"""
    schedule = rotation_engine.generate_schedule(
        start_date=rotation_start,
        end_date=rotation_start + timedelta(days=4)
    )
    
    shifts = schedule.get_all_shifts()
    validator = rotation_engine.shift_allocator.validator
    
    for shift in shifts:
        if shift.assigned_doctor_id:
            doctor = rotation_engine.shift_allocator._get_doctor_by_id(
                shift.assigned_doctor_id
            )
            # Check gender requirements
            assert validator.validate_gender_requirement(shift, doctor)
            # Check team rotation
            assert validator.validate_team_rotation(shift, doctor)
            # Check consecutive shifts
            assert validator.validate_consecutive_shifts(
                doctor,
                shift,
                [s for s in shifts if s != shift]
            )

def test_schedule_continuity(rotation_engine, rotation_start):
    """Test that schedules can be generated continuously"""
    # Generate first week
    week1_end = rotation_start + timedelta(days=4)
    schedule1 = rotation_engine.generate_schedule(
        start_date=rotation_start,
        end_date=week1_end
    )
    
    # Generate second week
    week2_start = week1_end + timedelta(days=3)  # Skip weekend
    week2_end = week2_start + timedelta(days=4)
    schedule2 = rotation_engine.generate_schedule(
        start_date=week2_start,
        end_date=week2_end
    )
    
    # Both schedules should have shifts
    assert len(schedule1.get_all_shifts()) > 0
    assert len(schedule2.get_all_shifts()) > 0
    
    # No overlap in shifts
    schedule1_shifts = set(s.id for s in schedule1.get_all_shifts())
    schedule2_shifts = set(s.id for s in schedule2.get_all_shifts())
    assert not schedule1_shifts.intersection(schedule2_shifts)

def test_aggressive_optimization_strategy():
    """Test the aggressive optimization strategy"""
    # Setup test data
    shift_allocator = MockShiftAllocator()
    equity_tracker = MockEquityTracker()
    shift_validator = MockShiftValidator()
    strategy = AggressiveOptimizationStrategy(shift_allocator, equity_tracker, shift_validator)
    
    # Create a test schedule with some suboptimal assignments
    schedule = Schedule()
    
    # Add shifts with suboptimal assignments
    shifts = [
        Shift(id="1", shift_definition=ShiftDefinition(shift_type="AM"), date=date(2024, 1, 1),
              assigned_doctor_id="doc1"),
        Shift(id="2", shift_definition=ShiftDefinition(shift_type="PM"), date=date(2024, 1, 1),
              assigned_doctor_id="doc2"),
        Shift(id="3", shift_definition=ShiftDefinition(shift_type="AM"), date=date(2024, 1, 2),
              assigned_doctor_id="doc3"),
        Shift(id="4", shift_definition=ShiftDefinition(shift_type="PM"), date=date(2024, 1, 2),
              assigned_doctor_id="doc4")
    ]
    
    for shift in shifts:
        schedule.add_shift(shift)
    
    # Run optimization
    optimized = strategy.optimize(schedule)
    
    # Verify optimization results
    assert len(optimized.get_all_shifts()) == len(shifts), "Should maintain same number of shifts"
    assert all(s.assigned_doctor_id for s in optimized.get_all_shifts()), "All shifts should be assigned"
    
    # Test block optimization
    blocks = strategy._group_shifts_into_blocks(shifts)
    assert len(blocks) > 0, "Should identify shift blocks"
    assert all(len(block) > 0 for block in blocks), "All blocks should have shifts"
    
    # Test team workload optimization
    team_shifts = {"A": 0, "B": 0}
    for shift in optimized.get_all_shifts():
        if shift.assigned_doctor_id:
            doctor = shift_allocator.get_doctor_by_id(shift.assigned_doctor_id)
            team_shifts[doctor.team] += 1
    
    # Team balance should be reasonable
    assert abs(team_shifts["A"] - team_shifts["B"]) <= 2, "Teams should be reasonably balanced"

def test_aggressive_optimization_performance():
    """Test performance of aggressive optimization"""
    shift_allocator = MockShiftAllocator()
    equity_tracker = MockEquityTracker()
    shift_validator = MockShiftValidator()
    strategy = AggressiveOptimizationStrategy(shift_allocator, equity_tracker, shift_validator)
    
    # Create a larger test schedule
    schedule = Schedule()
    start_date = date(2024, 1, 1)
    
    # Add 20 days of shifts (40 shifts total)
    for i in range(20):
        current_date = start_date + timedelta(days=i)
        am_shift = Shift(
            id=f"am_{i}",
            shift_definition=ShiftDefinition(shift_type="AM"),
            date=current_date,
            assigned_doctor_id=f"doc{i % 4 + 1}"
        )
        pm_shift = Shift(
            id=f"pm_{i}",
            shift_definition=ShiftDefinition(shift_type="PM"),
            date=current_date,
            assigned_doctor_id=f"doc{(i + 2) % 4 + 1}"
        )
        schedule.add_shift(am_shift)
        schedule.add_shift(pm_shift)
    
    # Measure optimization time
    start_time = time.time()
    optimized = strategy.optimize(schedule)
    end_time = time.time()
    
    # Verify performance
    optimization_time = end_time - start_time
    assert optimization_time < 5.0, f"Optimization took {optimization_time:.2f}s, should be under 5s"
    
    # Verify optimization quality
    initial_metrics = OptimizationMetrics.calculate_from_schedule(
        schedule, equity_tracker, shift_validator
    )
    final_metrics = OptimizationMetrics.calculate_from_schedule(
        optimized, equity_tracker, shift_validator
    )
    
    assert final_metrics.total_score > initial_metrics.total_score, \
        "Optimization should improve schedule quality"

def test_aggressive_optimization_constraints():
    """Test that aggressive optimization respects constraints"""
    shift_allocator = MockShiftAllocator()
    equity_tracker = MockEquityTracker()
    shift_validator = MockShiftValidator()
    strategy = AggressiveOptimizationStrategy(shift_allocator, equity_tracker, shift_validator)
    
    # Create a schedule with potential constraint violations
    schedule = Schedule()
    
    # Add shifts that could violate constraints if not careful
    shifts = [
        # Two consecutive shifts for same doctor
        Shift(id="1", shift_definition=ShiftDefinition(shift_type="AM"), date=date(2024, 1, 1),
              assigned_doctor_id="doc1"),
        Shift(id="2", shift_definition=ShiftDefinition(shift_type="PM"), date=date(2024, 1, 1),
              assigned_doctor_id="doc1"),
        # Gender requirement shift
        Shift(id="3", shift_definition=ShiftDefinition(shift_type="AM", gender_requirement="F"),
              date=date(2024, 1, 2), assigned_doctor_id="doc2"),
        # Preference violation shift
        Shift(id="4", shift_definition=ShiftDefinition(shift_type="PM"), date=date(2024, 1, 2),
              assigned_doctor_id="doc3")
    ]
    
    for shift in shifts:
        schedule.add_shift(shift)
    
    # Run optimization
    optimized = strategy.optimize(schedule)
    
    # Verify constraints are respected
    assert len(shift_validator.validate_schedule(optimized)) == 0, \
        "Optimized schedule should have no constraint violations"
    
    # Check specific constraints
    for i, shift1 in enumerate(optimized.get_all_shifts()):
        for shift2 in optimized.get_all_shifts()[i+1:]:
            if shift1.date == shift2.date:
                # No doctor should have consecutive shifts
                assert shift1.assigned_doctor_id != shift2.assigned_doctor_id, \
                    "No consecutive shifts for same doctor"
        
        # Gender requirements should be met
        if shift1.shift_definition.gender_requirement:
            doctor = shift_allocator.get_doctor_by_id(shift1.assigned_doctor_id)
            assert doctor.gender == shift1.shift_definition.gender_requirement, \
                "Gender requirements should be respected"

class MockDoctor:
    def __init__(self, id: str, team: str = "A", gender: str = "F", preferences: List[str] = None):
        self.id = id
        self.team = team
        self.gender = gender
        self.preferences = preferences or []

class MockShiftAllocator:
    def __init__(self):
        self.staff_loader = self
        self._doctors = {
            "doc1": MockDoctor("doc1", "A", "M", ["AM"]),
            "doc2": MockDoctor("doc2", "B", "F", ["PM"]),
            "doc3": MockDoctor("doc3", "A", "F", ["AM"]),
            "doc4": MockDoctor("doc4", "B", "M", ["PM"])
        }
    
    def get_doctor_by_id(self, doctor_id: str) -> MockDoctor:
        return self._doctors.get(doctor_id)
    
    def load_all_staff(self) -> List[MockDoctor]:
        return list(self._doctors.values())
    
    def is_doctor_eligible(self, doctor: MockDoctor, shift: Shift) -> bool:
        # Basic eligibility checks
        if shift.shift_definition.gender_requirement and doctor.gender != shift.shift_definition.gender_requirement:
            return False
        return True

class MockEquityTracker:
    def calculate_equity_score(self, schedule: Schedule) -> float:
        # Simple mock implementation
        return 0.8  # Reasonable equity score
    
    def get_next_eligible(self, doctors: List[MockDoctor]) -> Optional[MockDoctor]:
        return doctors[0] if doctors else None

class MockShiftValidator:
    def validate_schedule(self, schedule: Schedule) -> List[str]:
        # Simple mock implementation - no violations
        return []

class ShiftDefinition:
    def __init__(self, shift_type: str, gender_requirement: str = None):
        self.shift_type = shift_type
        self.gender_requirement = gender_requirement 