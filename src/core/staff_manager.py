from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Doctor:
    id: str
    name: str
    gender: str
    team: int

class StaffManager:
    def __init__(self):
        self._doctors: Dict[str, Doctor] = {}

    def add_doctor(self, doctor: Doctor) -> None:
        self._doctors[doctor.id] = doctor

    def get_doctor(self, doctor_id: str) -> Optional[Doctor]:
        return self._doctors.get(doctor_id)

    def get_team_doctors(self, team_number: int) -> List[Doctor]:
        return [doctor for doctor in self._doctors.values() if doctor.team == team_number] 