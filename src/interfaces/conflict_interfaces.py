from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date
from enum import Enum

class ConflictType(Enum):
    GENDER_REQUIREMENT = "gender_requirement"
    CONSECUTIVE_SHIFTS = "consecutive_shifts"
    TEAM_BALANCE = "team_balance"
    STAFF_UNAVAILABLE = "staff_unavailable"
    PREFERENCE_VIOLATION = "preference_violation"
    WORKLOAD_IMBALANCE = "workload_imbalance"

class ConflictSeverity(Enum):
    CRITICAL = "critical"  # Must be resolved
    HIGH = "high"         # Should be resolved
    MEDIUM = "medium"     # Better to resolve
    LOW = "low"          # Optional to resolve

class ConflictResolution(Enum):
    SWAP_STAFF = "swap_staff"
    REASSIGN_SHIFT = "reassign_shift"
    OVERRIDE_CONSTRAINT = "override_constraint"
    MANUAL_RESOLVE = "manual_resolve"

class Conflict:
    def __init__(self, 
                 conflict_type: ConflictType,
                 severity: ConflictSeverity,
                 description: str,
                 affected_shifts: List[Dict[str, Any]],
                 affected_staff: List[str],
                 possible_resolutions: List[Dict[str, Any]],
                 metrics: Dict[str, Any]):
        self.conflict_type = conflict_type
        self.severity = severity
        self.description = description
        self.affected_shifts = affected_shifts
        self.affected_staff = affected_staff
        self.possible_resolutions = possible_resolutions
        self.metrics = metrics

class IConflictResolver(ABC):
    @abstractmethod
    def detect_conflicts(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Detect all conflicts in the schedule"""
        pass
    
    @abstractmethod
    def analyze_conflict(self, conflict: Conflict) -> Dict[str, Any]:
        """Provide detailed analysis of a specific conflict"""
        pass
    
    @abstractmethod
    def suggest_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest possible resolutions for a conflict"""
        pass
    
    @abstractmethod
    def apply_resolution(self, conflict: Conflict, resolution: Dict[str, Any]) -> bool:
        """Apply a selected resolution to the schedule"""
        pass
    
    @abstractmethod
    def get_distribution_metrics(self, 
                               schedule: Dict[str, Any],
                               start_date: date,
                               end_date: date) -> Dict[str, Any]:
        """Get shift distribution metrics for a date range"""
        pass
    
    @abstractmethod
    def validate_manual_resolution(self, 
                                 conflict: Conflict,
                                 proposed_changes: Dict[str, Any]) -> List[str]:
        """Validate proposed manual changes"""
        pass
    
    @abstractmethod
    def get_staff_impact(self, 
                        conflict: Conflict,
                        resolution: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact of resolution on affected staff"""
        pass
    
    @abstractmethod
    def get_resolution_history(self, 
                             schedule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get history of applied conflict resolutions"""
        pass 