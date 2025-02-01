import pytest
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional
import tempfile
import json
import openpyxl
from io import BytesIO
from src.interfaces.audit_logger import IAuditLogger, ShiftAllocation
from src.core.audit_logger import AuditLogger, AuditEvent, AuditEventType, AuditEventSeverity
from src.models.doctor import Doctor
from src.models.shift import Shift
from src.models.doctor_stats import DoctorStats

@dataclass
class MockDoctor(Doctor):
    id: str
    name: str
    gender: str
    team: str

@dataclass
class MockShift(Shift):
    id: str
    date: date
    shift_type: str
    gender_requirement: Optional[str] = None

@pytest.fixture
def temp_log_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def audit_logger(temp_log_dir):
    return AuditLogger(log_dir=temp_log_dir)

@pytest.fixture
def sample_allocation():
    doctor = MockDoctor(id="D1", name="Dr. Smith", gender="F", team="A")
    shift = MockShift(id="S1", date=date(2024, 1, 1), shift_type="Day")
    stats = DoctorStats(total_shifts=10, night_shifts=3, weekend_shifts=2)
    
    return ShiftAllocation(
        timestamp=datetime.now(),
        doctor=doctor,
        shift=shift,
        gender_compliant=True,
        team_compliant=True,
        equity_stats=stats
    )

def test_log_allocation_stores_data(audit_logger, sample_allocation, temp_log_dir):
    """Test that logging an allocation properly stores the data"""
    audit_logger.log_allocation(sample_allocation)
    
    # Verify JSON file was created and contains correct data
    log_file = f"{temp_log_dir}/{sample_allocation.shift.date.strftime('%Y-%m-%d')}.json"
    with open(log_file, 'r') as f:
        allocations = json.load(f)
        assert len(allocations) == 1
        alloc = allocations[0]
        assert alloc["doctor_id"] == "D1"
        assert alloc["doctor_name"] == "Dr. Smith"
        assert alloc["shift_type"] == "Day"
        assert alloc["gender_compliant"] is True
        assert alloc["team_compliant"] is True
        assert alloc["total_shifts"] == 10
        assert alloc["night_shifts"] == 3
        assert alloc["weekend_shifts"] == 2

def test_generate_daily_report_format(audit_logger, sample_allocation):
    """Test that daily report is generated in correct Excel format"""
    audit_logger.log_allocation(sample_allocation)
    report_bytes = audit_logger.generate_daily_report(sample_allocation.shift.date)
    
    # Load Excel file and verify structure
    wb = openpyxl.load_workbook(BytesIO(report_bytes))
    ws = wb.active
    assert ws.title == "Daily Schedule"
    
    # Check headers
    expected_headers = ["Time", "Doctor", "Shift Type", "Gender Compliant", 
                       "Team Compliant", "Total Shifts", "Night Shifts", "Weekend Shifts"]
    for col, header in enumerate(expected_headers, 1):
        assert ws.cell(row=1, column=col).value == header
    
    # Check data row
    assert ws.cell(row=2, column=2).value == "Dr. Smith"
    assert ws.cell(row=2, column=3).value == "Day"
    assert ws.cell(row=2, column=4).value == "Yes"
    assert ws.cell(row=2, column=5).value == "Yes"
    assert ws.cell(row=2, column=6).value == 10
    assert ws.cell(row=2, column=7).value == 3
    assert ws.cell(row=2, column=8).value == 2

def test_generate_distribution_report(audit_logger, sample_allocation):
    """Test that distribution report shows correct equity metrics"""
    # Log multiple allocations
    audit_logger.log_allocation(sample_allocation)
    
    # Generate report for date range
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 7)
    report_bytes = audit_logger.generate_distribution_report(start_date, end_date)
    
    # Verify report structure
    wb = openpyxl.load_workbook(BytesIO(report_bytes))
    ws = wb.active
    assert ws.title == "Distribution Report"
    
    # Check headers
    expected_headers = ["Doctor", "Total Shifts", "Night Shifts", "Weekend Shifts",
                       "Gender Compliance %", "Team Compliance %"]
    for col, header in enumerate(expected_headers, 1):
        assert ws.cell(row=1, column=col).value == header
    
    # Check data row
    assert ws.cell(row=2, column=1).value == "Dr. Smith"
    assert ws.cell(row=2, column=2).value == 1  # One allocation
    assert ws.cell(row=2, column=5).value == "100.0%"  # Full compliance
    assert ws.cell(row=2, column=6).value == "100.0%"  # Full compliance

class TestAuditLogger:
    @pytest.fixture
    def audit_logger(self):
        return AuditLogger()
    
    def test_log_schedule_generation(self, audit_logger):
        """Test logging of schedule generation events"""
        event = audit_logger.log_schedule_generation(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 7),
            num_shifts=35,
            success=True
        )
        
        assert event.event_type == AuditEventType.SCHEDULE_GENERATION
        assert event.severity == AuditEventSeverity.INFO
        assert event.timestamp is not None
        assert "Generated schedule" in event.description
        assert event.details["num_shifts"] == 35
        assert event.details["success"] is True
    
    def test_log_optimization_step(self, audit_logger):
        """Test logging of optimization steps"""
        event = audit_logger.log_optimization_step(
            iteration=1,
            strategy="equity",
            improvement=0.15,
            metrics={"equity_score": 0.85}
        )
        
        assert event.event_type == AuditEventType.OPTIMIZATION
        assert event.severity == AuditEventSeverity.INFO
        assert "Optimization step" in event.description
        assert event.details["iteration"] == 1
        assert event.details["strategy"] == "equity"
        assert event.details["improvement"] == 0.15
    
    def test_log_constraint_violation(self, audit_logger):
        """Test logging of constraint violations"""
        event = audit_logger.log_constraint_violation(
            constraint_type="gender_requirement",
            shift_id="TRIAGE_MON_AM",
            severity=AuditEventSeverity.ERROR,
            details={"required_gender": "F", "assigned_gender": "M"}
        )
        
        assert event.event_type == AuditEventType.CONSTRAINT_VIOLATION
        assert event.severity == AuditEventSeverity.ERROR
        assert "Constraint violation" in event.description
        assert event.details["constraint_type"] == "gender_requirement"
        assert event.details["shift_id"] == "TRIAGE_MON_AM"
    
    def test_log_conflict_resolution(self, audit_logger):
        """Test logging of conflict resolution events"""
        event = audit_logger.log_conflict_resolution(
            conflict_id="CONFLICT_001",
            resolution_type="swap_shifts",
            success=True,
            affected_shifts=["SHIFT_1", "SHIFT_2"]
        )
        
        assert event.event_type == AuditEventType.CONFLICT_RESOLUTION
        assert event.severity == AuditEventSeverity.INFO
        assert "Conflict resolution" in event.description
        assert event.details["conflict_id"] == "CONFLICT_001"
        assert event.details["success"] is True
    
    def test_log_performance_metric(self, audit_logger):
        """Test logging of performance metrics"""
        event = audit_logger.log_performance_metric(
            metric_name="schedule_generation_time",
            value=2.5,
            unit="seconds"
        )
        
        assert event.event_type == AuditEventType.PERFORMANCE
        assert event.severity == AuditEventSeverity.INFO
        assert "Performance metric" in event.description
        assert event.details["metric_name"] == "schedule_generation_time"
        assert event.details["value"] == 2.5
        assert event.details["unit"] == "seconds"
    
    def test_get_events_by_type(self, audit_logger):
        """Test retrieving events by type"""
        # Log some events
        audit_logger.log_performance_metric("metric1", 1.0, "seconds")
        audit_logger.log_performance_metric("metric2", 2.0, "seconds")
        audit_logger.log_constraint_violation("gender", "SHIFT_1", AuditEventSeverity.ERROR, {})
        
        # Get performance events
        performance_events = audit_logger.get_events_by_type(AuditEventType.PERFORMANCE)
        assert len(performance_events) == 2
        assert all(e.event_type == AuditEventType.PERFORMANCE for e in performance_events)
    
    def test_get_events_by_severity(self, audit_logger):
        """Test retrieving events by severity"""
        # Log events with different severities
        audit_logger.log_constraint_violation("type1", "SHIFT_1", AuditEventSeverity.ERROR, {})
        audit_logger.log_constraint_violation("type2", "SHIFT_2", AuditEventSeverity.WARNING, {})
        audit_logger.log_performance_metric("metric1", 1.0, "seconds")  # INFO severity
        
        # Get error events
        error_events = audit_logger.get_events_by_severity(AuditEventSeverity.ERROR)
        assert len(error_events) == 1
        assert all(e.severity == AuditEventSeverity.ERROR for e in error_events)
    
    def test_get_events_in_timerange(self, audit_logger):
        """Test retrieving events within a time range"""
        # Log events at different times
        start_time = datetime(2024, 1, 1, 10, 0)
        end_time = datetime(2024, 1, 1, 11, 0)
        
        audit_logger._override_timestamp(datetime(2024, 1, 1, 9, 59))  # Before range
        audit_logger.log_performance_metric("metric1", 1.0, "seconds")
        
        audit_logger._override_timestamp(datetime(2024, 1, 1, 10, 30))  # Within range
        audit_logger.log_performance_metric("metric2", 2.0, "seconds")
        
        audit_logger._override_timestamp(datetime(2024, 1, 1, 11, 1))  # After range
        audit_logger.log_performance_metric("metric3", 3.0, "seconds")
        
        # Get events in range
        events = audit_logger.get_events_in_timerange(start_time, end_time)
        assert len(events) == 1
        assert events[0].details["metric_name"] == "metric2"
    
    def test_export_to_excel(self, audit_logger, tmp_path):
        """Test exporting audit trail to Excel"""
        # Log some events
        audit_logger.log_schedule_generation(
            datetime(2024, 1, 1),
            datetime(2024, 1, 7),
            35,
            True
        )
        audit_logger.log_constraint_violation(
            "gender_requirement",
            "SHIFT_1",
            AuditEventSeverity.ERROR,
            {"required_gender": "F"}
        )
        
        # Export to Excel
        excel_path = tmp_path / "audit_trail.xlsx"
        audit_logger.export_to_excel(str(excel_path))
        
        # Verify file exists
        assert excel_path.exists()
        
        # TODO: Add verification of Excel content when implementing export_to_excel 