from typing import List
from src.interfaces.staff_interfaces import Doctor

class StaffDataLoader:
    """Service for loading staff data from configuration"""
    
    @staticmethod
    def load_team_1() -> List[Doctor]:
        """Load Team 1 doctors from configuration"""
        return [
            Doctor(id="M1", name="Raghid Altalebi", gender="M", team=1),
            Doctor(id="M2", name="Kashif Ali Raza", gender="M", team=1),
            Doctor(id="M3", name="Habeebullah Mohammed Abdul Latheef", gender="M", team=1),
            Doctor(id="M4", name="Mohamed Rizan Jameel", gender="M", team=1),
            Doctor(id="M5", name="Amer Habeeb", gender="M", team=1),
            Doctor(id="M6", name="Ahmed Mahmoud M Karmus", gender="M", team=1),
            Doctor(id="M7", name="Saqib Ahmad", gender="M", team=1),
            Doctor(id="M8", name="Ismail Nasry Hamdan Mahmoud", gender="M", team=1),
            Doctor(id="M9", name="Mohanad Al Helo", gender="M", team=1),
            Doctor(id="F1", name="Eman Hassan Khiri", gender="F", team=1),
            Doctor(id="F2", name="Alaa Salah AG AlSharei", gender="F", team=1),
            Doctor(id="F3", name="Sahar Alkurbi", gender="F", team=1),
            Doctor(id="F4", name="Safa Ahmed Elhag Elbashir", gender="F", team=1),
        ]
    
    @staticmethod
    def load_team_2() -> List[Doctor]:
        """Load Team 2 doctors from configuration"""
        return [
            Doctor(id="M10", name="Sahibzada", gender="M", team=2),
            Doctor(id="M11", name="Shahzad Ahmed", gender="M", team=2),
            Doctor(id="M12", name="Ijaz Ahmad", gender="M", team=2),
            Doctor(id="M13", name="Faisal Mahmood", gender="M", team=2),
            Doctor(id="M14", name="Zulqarnain Akhtar", gender="M", team=2),
            Doctor(id="M15", name="Wajid Hassan", gender="M", team=2),
            Doctor(id="M16", name="Mohamed Ali Kholeif Mokibel", gender="M", team=2),
            Doctor(id="M17", name="Tarif Kalash", gender="M", team=2),
            Doctor(id="F5", name="Robina Mohammad", gender="F", team=2),
            Doctor(id="F6", name="Farhana Islam", gender="F", team=2),
            Doctor(id="F7", name="Ilhaam Salim Abeid Abud", gender="F", team=2),
            Doctor(id="F8", name="Safa Hisham Mohamed Zain", gender="F", team=2),
            Doctor(id="F9", name="Inas Mahmoud Ibrahim Alnatour", gender="F", team=2),
        ]
    
    @staticmethod
    def load_all_staff() -> List[Doctor]:
        """Load all doctors from both teams"""
        return StaffDataLoader.load_team_1() + StaffDataLoader.load_team_2() 