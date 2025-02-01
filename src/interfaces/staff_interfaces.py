from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Doctor:
    id: str
    name: str
    gender: str
    team: int

class IStaffManager(ABC):
    @abstractmethod
    def add_doctor(self, doctor: Doctor) -> None:
        pass

    @abstractmethod
    def get_doctor(self, doctor_id: str) -> Optional[Doctor]:
        pass

    @abstractmethod
    def get_team_doctors(self, team_number: int) -> List[Doctor]:
        pass 