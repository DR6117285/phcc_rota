import json
import csv
from typing import List, Dict, Any
from datetime import datetime, date
import logging
from pathlib import Path

from ..interfaces.data_interfaces import IDataImporter

logger = logging.getLogger(__name__)

class ManualInputService(IDataImporter):
    """Service for importing data from manual input sources (CSV, JSON, Excel)"""
    
    SUPPORTED_FORMATS = ['csv', 'json', 'xlsx']
    
    def __init__(self):
        self.validation_errors = []
    
    def import_staff_data(self, source: str) -> List[Dict[str, Any]]:
        """Import staff data from the specified source"""
        file_format = Path(source).suffix[1:].lower()
        if file_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        try:
            if file_format == 'json':
                return self._import_json(source)
            elif file_format == 'csv':
                return self._import_csv(source)
            elif file_format == 'xlsx':
                return self._import_excel(source)
        except Exception as e:
            logger.error(f"Error importing staff data: {str(e)}")
            raise
    
    def import_shift_preferences(self, source: str) -> Dict[str, List[Dict[str, Any]]]:
        """Import shift preferences for staff members"""
        preferences = {}
        data = self.import_staff_data(source)
        
        for entry in data:
            staff_id = entry.get('staff_id')
            if staff_id and 'preferences' in entry:
                preferences[staff_id] = [
                    {
                        'date': datetime.strptime(pref['date'], '%Y-%m-%d').date(),
                        'shift_type': pref['shift_type']
                    }
                    for pref in entry['preferences']
                ]
        
        return preferences
    
    def import_leave_data(self, source: str) -> Dict[str, List[date]]:
        """Import leave dates for staff members"""
        leave_data = {}
        data = self.import_staff_data(source)
        
        for entry in data:
            staff_id = entry.get('staff_id')
            if staff_id and 'leave_dates' in entry:
                leave_data[staff_id] = [
                    datetime.strptime(leave_date, '%Y-%m-%d').date()
                    for leave_date in entry['leave_dates']
                ]
        
        return leave_data
    
    def import_team_assignments(self, source: str) -> Dict[str, str]:
        """Import team assignments for staff members"""
        team_assignments = {}
        data = self.import_staff_data(source)
        
        for entry in data:
            staff_id = entry.get('staff_id')
            team = entry.get('team')
            if staff_id and team:
                team_assignments[staff_id] = team
        
        return team_assignments
    
    def validate_import(self, data: Dict[str, Any]) -> List[str]:
        """Validate imported data and return list of validation errors"""
        self.validation_errors = []
        
        # Validate required fields
        required_fields = ['staff_id', 'name', 'gender']
        for entry in data.get('staff', []):
            missing_fields = [
                field for field in required_fields 
                if not entry.get(field)
            ]
            if missing_fields:
                self.validation_errors.append(
                    f"Missing required fields for staff member: {', '.join(missing_fields)}"
                )
        
        # Validate data types
        for entry in data.get('staff', []):
            if not isinstance(entry.get('staff_id'), str):
                self.validation_errors.append(
                    f"Invalid staff_id type for {entry.get('name')}"
                )
            
            if 'preferences' in entry and not isinstance(entry['preferences'], list):
                self.validation_errors.append(
                    f"Invalid preferences format for {entry.get('name')}"
                )
            
            if 'leave_dates' in entry and not isinstance(entry['leave_dates'], list):
                self.validation_errors.append(
                    f"Invalid leave_dates format for {entry.get('name')}"
                )
        
        # Validate date formats
        for entry in data.get('staff', []):
            if 'preferences' in entry:
                for pref in entry['preferences']:
                    try:
                        datetime.strptime(pref['date'], '%Y-%m-%d')
                    except (ValueError, KeyError):
                        self.validation_errors.append(
                            f"Invalid date format in preferences for {entry.get('name')}"
                        )
            
            if 'leave_dates' in entry:
                for leave_date in entry['leave_dates']:
                    try:
                        datetime.strptime(leave_date, '%Y-%m-%d')
                    except ValueError:
                        self.validation_errors.append(
                            f"Invalid leave date format for {entry.get('name')}"
                        )
        
        return self.validation_errors
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported import formats"""
        return self.SUPPORTED_FORMATS
    
    def _import_json(self, source: str) -> List[Dict[str, Any]]:
        """Import data from JSON file"""
        with open(source, 'r') as f:
            data = json.load(f)
            if self.validate_import(data):
                raise ValueError(
                    f"Validation errors: {', '.join(self.validation_errors)}"
                )
            return data.get('staff', [])
    
    def _import_csv(self, source: str) -> List[Dict[str, Any]]:
        """Import data from CSV file"""
        staff_data = []
        with open(source, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert preferences and leave_dates from string to list
                if 'preferences' in row:
                    try:
                        row['preferences'] = json.loads(row['preferences'])
                    except json.JSONDecodeError:
                        row['preferences'] = []
                
                if 'leave_dates' in row:
                    try:
                        row['leave_dates'] = json.loads(row['leave_dates'])
                    except json.JSONDecodeError:
                        row['leave_dates'] = []
                
                staff_data.append(row)
        
        if self.validate_import({'staff': staff_data}):
            raise ValueError(
                f"Validation errors: {', '.join(self.validation_errors)}"
            )
        return staff_data
    
    def _import_excel(self, source: str) -> List[Dict[str, Any]]:
        """Import data from Excel file"""
        try:
            import pandas as pd
            
            # Read all sheets
            xl = pd.ExcelFile(source)
            
            # Read staff data from main sheet
            staff_df = pd.read_excel(xl, 'Staff')
            staff_data = staff_df.to_dict('records')
            
            # Read preferences if sheet exists
            if 'Preferences' in xl.sheet_names:
                pref_df = pd.read_excel(xl, 'Preferences')
                preferences = pref_df.to_dict('records')
                
                # Merge preferences with staff data
                for staff in staff_data:
                    staff['preferences'] = [
                        pref for pref in preferences
                        if pref['staff_id'] == staff['staff_id']
                    ]
            
            # Read leave data if sheet exists
            if 'Leave' in xl.sheet_names:
                leave_df = pd.read_excel(xl, 'Leave')
                leave_data = leave_df.to_dict('records')
                
                # Merge leave data with staff data
                for staff in staff_data:
                    staff['leave_dates'] = [
                        leave['date'].strftime('%Y-%m-%d')
                        for leave in leave_data
                        if leave['staff_id'] == staff['staff_id']
                    ]
            
            if self.validate_import({'staff': staff_data}):
                raise ValueError(
                    f"Validation errors: {', '.join(self.validation_errors)}"
                )
            return staff_data
            
        except ImportError:
            logger.error("pandas is required for Excel import")
            raise
        except Exception as e:
            logger.error(f"Error importing Excel file: {str(e)}")
            raise 