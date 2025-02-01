from datetime import datetime, timedelta, time
from enum import Enum
from typing import Dict, Tuple

class RotationShift(str, Enum):
    """Represents AM or PM rotation"""
    AM = "AM"
    PM = "PM"

class RotationPattern:
    """Handles the two-week rotation pattern for teams"""
    
    WEEK_1_PATTERN = {
        0: (RotationShift.AM, RotationShift.PM),  # Sunday
        1: (RotationShift.AM, RotationShift.PM),  # Monday
        2: (RotationShift.AM, RotationShift.PM),  # Tuesday
        3: (RotationShift.PM, RotationShift.AM),  # Wednesday
        4: (RotationShift.PM, RotationShift.AM),  # Thursday
    }
    
    WEEK_2_PATTERN = {
        0: (RotationShift.PM, RotationShift.AM),  # Sunday
        1: (RotationShift.PM, RotationShift.AM),  # Monday
        2: (RotationShift.PM, RotationShift.AM),  # Tuesday
        3: (RotationShift.AM, RotationShift.PM),  # Wednesday
        4: (RotationShift.AM, RotationShift.PM),  # Thursday
    }
    
    def __init__(self, start_date: datetime):
        """Initialize with a start date for the rotation cycle"""
        self.start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_team_rotations(self, date: datetime) -> Dict[int, RotationShift]:
        """Get the rotation shifts for both teams on a given date
        
        Args:
            date: The date to get rotations for
            
        Returns:
            Dictionary mapping team number (1 or 2) to their rotation shift (AM/PM)
        """
        # Normalize date to start of day
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate days since start of rotation
        days_diff = (date - self.start_date).days
        
        # Get week number in rotation (0 or 1)
        week_in_rotation = (days_diff // 7) % 2
        
        # Get day of week (0-4, Sunday-Thursday)
        day_of_week = date.weekday()
        if day_of_week > 4:  # Friday or Saturday
            raise ValueError("No rotations on weekends")
            
        # Get pattern for current week
        pattern = self.WEEK_1_PATTERN if week_in_rotation == 0 else self.WEEK_2_PATTERN
        
        # Get team rotations for this day
        team1_rotation, team2_rotation = pattern[day_of_week]
        
        return {
            1: team1_rotation,
            2: team2_rotation
        }
    
    def is_team_on_am(self, team: int, date: datetime) -> bool:
        """Check if a team is on AM rotation for a given date"""
        rotations = self.get_team_rotations(date)
        return rotations[team] == RotationShift.AM
    
    def is_team_on_pm(self, team: int, date: datetime) -> bool:
        """Check if a team is on PM rotation for a given date"""
        rotations = self.get_team_rotations(date)
        return rotations[team] == RotationShift.PM
    
    def is_team_on_correct_rotation(self, team: int, date: datetime, time_slot: 'TimeSlot') -> bool:
        """Check if a team is on the correct rotation for a given time slot
        
        Args:
            team: Team number (1 or 2)
            date: The date to check
            time_slot: The time slot to check
            
        Returns:
            True if the team is on the correct rotation for the time slot
        """
        # Special case: 2pm-8pm shifts require one doctor from each team
        if time_slot.start_time == time(14) and time_slot.end_time == time(20):
            return True
            
        # AM shifts (before noon) should be taken by AM rotation team
        if time_slot.start_time.hour < 12:
            return self.is_team_on_am(team, date)
        # PM shifts (noon onwards) should be taken by PM rotation team
        else:
            return self.is_team_on_pm(team, date) 