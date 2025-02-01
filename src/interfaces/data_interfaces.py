from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date

class IDataImporter(ABC):
    @abstractmethod
    def import_staff_data(self, source: str) -> List[Dict[str, Any]]:
        """Import staff data from the specified source"""
        pass
    
    @abstractmethod
    def import_shift_preferences(self, source: str) -> Dict[str, List[Dict[str, Any]]]:
        """Import shift preferences for staff members"""
        pass
    
    @abstractmethod
    def import_leave_data(self, source: str) -> Dict[str, List[date]]:
        """Import leave dates for staff members"""
        pass
    
    @abstractmethod
    def import_team_assignments(self, source: str) -> Dict[str, str]:
        """Import team assignments for staff members"""
        pass
    
    @abstractmethod
    def validate_import(self, data: Dict[str, Any]) -> List[str]:
        """Validate imported data and return list of validation errors"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported import formats"""
        pass 