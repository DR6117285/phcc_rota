from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class SkillLevel(Enum):
    TRAINEE = "TRAINEE"
    JUNIOR = "JUNIOR"
    SENIOR = "SENIOR"
    EXPERT = "EXPERT"

class StaffManagementService:
    def __init__(self):
        self.staff_profiles = {}
        self.teams = {}
        self.skills_registry = set()
        self.certifications_registry = set()
    
    def add_staff_member(self, staff_data: Dict) -> str:
        """Add a new staff member to the system."""
        try:
            staff_id = staff_data.get('id') or f"STAFF_{len(self.staff_profiles) + 1}"
            if staff_id in self.staff_profiles:
                raise ValueError(f"Staff member with ID {staff_id} already exists")
            
            # Validate required fields
            required_fields = ['name', 'gender', 'role']
            for field in required_fields:
                if field not in staff_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create staff profile
            staff_profile = {
                'id': staff_id,
                'name': staff_data['name'],
                'gender': staff_data['gender'],
                'role': staff_data['role'],
                'team': staff_data.get('team'),
                'skills': {},  # Dict[skill_name, SkillLevel]
                'certifications': set(),  # Set of certification names
                'preferences': {
                    'shift_types': set(),  # Preferred shift types
                    'days': set(),  # Preferred days
                    'colleagues': set(),  # Preferred colleagues to work with
                },
                'availability': {
                    'regular': set(),  # Regular available days
                    'exceptions': {
                        'unavailable': set(),  # Specific unavailable dates
                        'available': set(),  # Override regular unavailability
                    }
                },
                'contact': {
                    'email': staff_data.get('email'),
                    'phone': staff_data.get('phone'),
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            
            self.staff_profiles[staff_id] = staff_profile
            
            # Add to team if specified
            if staff_data.get('team'):
                self.assign_to_team(staff_id, staff_data['team'])
            
            logger.info(f"Added new staff member: {staff_id}")
            return staff_id
            
        except Exception as e:
            logger.error(f"Error adding staff member: {str(e)}")
            raise

    def update_staff_member(self, staff_id: str, updates: Dict) -> Dict:
        """Update a staff member's information."""
        try:
            if staff_id not in self.staff_profiles:
                raise ValueError(f"Staff member not found: {staff_id}")
            
            profile = self.staff_profiles[staff_id]
            
            # Handle special update cases
            if 'team' in updates and updates['team'] != profile['team']:
                self.assign_to_team(staff_id, updates['team'])
            
            # Update basic fields
            updateable_fields = ['name', 'gender', 'role', 'email', 'phone']
            for field in updateable_fields:
                if field in updates:
                    if field in ['email', 'phone']:
                        profile['contact'][field] = updates[field]
                    else:
                        profile[field] = updates[field]
            
            profile['updated_at'] = datetime.now()
            logger.info(f"Updated staff member: {staff_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error updating staff member: {str(e)}")
            raise

    def add_skill(self, staff_id: str, skill_name: str, level: SkillLevel) -> None:
        """Add or update a skill for a staff member."""
        try:
            if staff_id not in self.staff_profiles:
                raise ValueError(f"Staff member not found: {staff_id}")
            
            self.skills_registry.add(skill_name)
            self.staff_profiles[staff_id]['skills'][skill_name] = level
            self.staff_profiles[staff_id]['updated_at'] = datetime.now()
            
            logger.info(f"Added skill {skill_name} ({level}) to staff member: {staff_id}")
            
        except Exception as e:
            logger.error(f"Error adding skill: {str(e)}")
            raise

    def add_certification(self, staff_id: str, certification: str, expiry_date: Optional[datetime] = None) -> None:
        """Add a certification for a staff member."""
        try:
            if staff_id not in self.staff_profiles:
                raise ValueError(f"Staff member not found: {staff_id}")
            
            self.certifications_registry.add(certification)
            self.staff_profiles[staff_id]['certifications'].add(certification)
            self.staff_profiles[staff_id]['updated_at'] = datetime.now()
            
            logger.info(f"Added certification {certification} to staff member: {staff_id}")
            
        except Exception as e:
            logger.error(f"Error adding certification: {str(e)}")
            raise

    def update_availability(self, staff_id: str, availability_type: str, dates: Set[datetime], is_available: bool) -> None:
        """Update a staff member's availability."""
        try:
            if staff_id not in self.staff_profiles:
                raise ValueError(f"Staff member not found: {staff_id}")
            
            profile = self.staff_profiles[staff_id]
            
            if availability_type == 'regular':
                if is_available:
                    profile['availability']['regular'].update(dates)
                else:
                    profile['availability']['regular'].difference_update(dates)
            else:
                exception_type = 'available' if is_available else 'unavailable'
                profile['availability']['exceptions'][exception_type].update(dates)
            
            profile['updated_at'] = datetime.now()
            logger.info(f"Updated availability for staff member: {staff_id}")
            
        except Exception as e:
            logger.error(f"Error updating availability: {str(e)}")
            raise

    def update_preferences(self, staff_id: str, preference_type: str, preferences: Set[str]) -> None:
        """Update a staff member's preferences."""
        try:
            if staff_id not in self.staff_profiles:
                raise ValueError(f"Staff member not found: {staff_id}")
            
            if preference_type not in ['shift_types', 'days', 'colleagues']:
                raise ValueError(f"Invalid preference type: {preference_type}")
            
            profile = self.staff_profiles[staff_id]
            profile['preferences'][preference_type] = preferences
            profile['updated_at'] = datetime.now()
            
            logger.info(f"Updated {preference_type} preferences for staff member: {staff_id}")
            
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            raise

    def assign_to_team(self, staff_id: str, team_id: str) -> None:
        """Assign a staff member to a team."""
        try:
            if staff_id not in self.staff_profiles:
                raise ValueError(f"Staff member not found: {staff_id}")
            
            # Remove from current team if any
            current_team = self.staff_profiles[staff_id].get('team')
            if current_team and current_team in self.teams:
                self.teams[current_team].remove(staff_id)
            
            # Add to new team
            if team_id not in self.teams:
                self.teams[team_id] = set()
            self.teams[team_id].add(staff_id)
            
            # Update staff profile
            self.staff_profiles[staff_id]['team'] = team_id
            self.staff_profiles[staff_id]['updated_at'] = datetime.now()
            
            logger.info(f"Assigned staff member {staff_id} to team: {team_id}")
            
        except Exception as e:
            logger.error(f"Error assigning to team: {str(e)}")
            raise

    def get_staff_member(self, staff_id: str) -> Dict:
        """Get a staff member's complete profile."""
        try:
            if staff_id not in self.staff_profiles:
                raise ValueError(f"Staff member not found: {staff_id}")
            
            return self.staff_profiles[staff_id]
            
        except Exception as e:
            logger.error(f"Error getting staff member: {str(e)}")
            raise

    def get_team_members(self, team_id: str) -> List[Dict]:
        """Get all members of a team."""
        try:
            if team_id not in self.teams:
                raise ValueError(f"Team not found: {team_id}")
            
            return [self.staff_profiles[staff_id] for staff_id in self.teams[team_id]]
            
        except Exception as e:
            logger.error(f"Error getting team members: {str(e)}")
            raise

    def get_available_staff(self, date: datetime, shift_type: Optional[str] = None) -> List[Dict]:
        """Get all staff members available for a given date and shift type."""
        try:
            available_staff = []
            
            for staff_id, profile in self.staff_profiles.items():
                # Check regular availability
                if date.weekday() not in profile['availability']['regular']:
                    continue
                
                # Check exceptions
                if date in profile['availability']['exceptions']['unavailable']:
                    continue
                
                # Check shift type preference if specified
                if shift_type and shift_type not in profile['preferences']['shift_types']:
                    continue
                
                available_staff.append(profile)
            
            return available_staff
            
        except Exception as e:
            logger.error(f"Error getting available staff: {str(e)}")
            raise

    def get_staff_with_skill(self, skill_name: str, min_level: Optional[SkillLevel] = None) -> List[Dict]:
        """Get all staff members with a specific skill at or above the minimum level."""
        try:
            qualified_staff = []
            
            for staff_id, profile in self.staff_profiles.items():
                if skill_name in profile['skills']:
                    if not min_level or profile['skills'][skill_name].value >= min_level.value:
                        qualified_staff.append(profile)
            
            return qualified_staff
            
        except Exception as e:
            logger.error(f"Error getting staff with skill: {str(e)}")
            raise

    def get_staff_with_certification(self, certification: str) -> List[Dict]:
        """Get all staff members with a specific certification."""
        try:
            certified_staff = []
            
            for staff_id, profile in self.staff_profiles.items():
                if certification in profile['certifications']:
                    certified_staff.append(profile)
            
            return certified_staff
            
        except Exception as e:
            logger.error(f"Error getting staff with certification: {str(e)}")
            raise 