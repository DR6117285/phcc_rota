from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

class AuditEventType(Enum):
    """Types of audit events"""
    SCHEDULE_GENERATION = auto()
    OPTIMIZATION = auto()
    CONSTRAINT_VIOLATION = auto()
    CONFLICT_RESOLUTION = auto()
    PERFORMANCE = auto()

class AuditEventSeverity(Enum):
    """Severity levels for audit events"""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class AuditEvent:
    """Represents a single audit event"""
    event_type: AuditEventType
    severity: AuditEventSeverity
    timestamp: datetime
    description: str
    details: Dict[str, Any]

class IAuditLogger(ABC):
    """Interface for audit logging functionality"""
    
    @abstractmethod
    def log_schedule_generation(self, 
                              start_date: datetime,
                              end_date: datetime,
                              num_shifts: int,
                              success: bool) -> AuditEvent:
        """Log a schedule generation event"""
        pass
    
    @abstractmethod
    def log_optimization_step(self,
                            iteration: int,
                            strategy: str,
                            improvement: float,
                            metrics: Dict[str, float]) -> AuditEvent:
        """Log an optimization step"""
        pass
    
    @abstractmethod
    def log_constraint_violation(self,
                               constraint_type: str,
                               shift_id: str,
                               severity: AuditEventSeverity,
                               details: Dict[str, Any]) -> AuditEvent:
        """Log a constraint violation"""
        pass
    
    @abstractmethod
    def log_conflict_resolution(self,
                              conflict_id: str,
                              resolution_type: str,
                              success: bool,
                              affected_shifts: List[str]) -> AuditEvent:
        """Log a conflict resolution event"""
        pass
    
    @abstractmethod
    def log_performance_metric(self,
                             metric_name: str,
                             value: float,
                             unit: str) -> AuditEvent:
        """Log a performance metric"""
        pass
    
    @abstractmethod
    def get_events_by_type(self, event_type: AuditEventType) -> List[AuditEvent]:
        """Get all events of a specific type"""
        pass
    
    @abstractmethod
    def get_events_by_severity(self, severity: AuditEventSeverity) -> List[AuditEvent]:
        """Get all events of a specific severity"""
        pass
    
    @abstractmethod
    def get_events_in_timerange(self,
                              start_time: datetime,
                              end_time: datetime) -> List[AuditEvent]:
        """Get all events within a specific time range"""
        pass
    
    @abstractmethod
    def export_to_excel(self, filepath: str) -> None:
        """Export audit trail to Excel file"""
        pass 