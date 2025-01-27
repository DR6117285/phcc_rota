# Medical Facility Rota Scheduling System

## Overview
This document outlines the requirements for an automated rota scheduling system for a medical facility operating Sunday through Thursday. The system must handle two teams of doctors, gender-specific shift requirements, and maintain equitable shift distribution while prioritizing essential coverage.

## Staff Structure

### Team 1
| ID | Name | Gender |
|----|------|--------|
| M1 | Raghid Altalebi | M |
| M2 | Kashif Ali Raza | M |
| M3 | Habeebullah Mohammed Abdul Latheef | M |
| M4 | Mohamed Rizan Jameel | M |
| M5 | Amer Habeeb | M |
| M6 | Ahmed Mahmoud M Karmus | M |
| M7 | Saqib Ahmad | M |
| M8 | Ismail Nasry Hamdan Mahmoud | M |
| M9 | Mohanad Al Helo | M |
| F1 | Eman Hassan Khiri | F |
| F2 | Alaa Salah AG AlSharei | F |
| F3 | Sahar Alkurbi | F |
| F4 | Safa Ahmed Elhag Elbashir | F |

### Team 2
| ID | Name | Gender |
|----|------|--------|
| M10 | Sahibzada | M |
| M11 | Shahzad Ahmed | M |
| M12 | Ijaz Ahmad | M |
| M13 | Faisal Mahmood | M |
| M14 | Zulqarnain Akhtar | M |
| M15 | Wajid Hassan | M |
| M16 | Mohamed Ali Kholeif Mokibel | M |
| M17 | Tarif Kalash | M |
| F5 | Robina Mohammad | F |
| F6 | Farhana Islam | F |
| F7 | Ilhaam Salim Abeid Abud | F |
| F8 | Safa Hisham Mohamed Zain | F |
| F9 | Inas Mahmoud Ibrahim Alnatour | F |

## Shift Requirements

### Essential Shifts (Must Be Filled)
| Shift | Time | Gender Requirement |
|-------|------|-------------------|
| WBC | 7am - 2pm | Male Only |
| WBC | 4pm - 10pm | Male Only |
| TRIAGE | 9am - 4pm | Male Only |
| TRIAGE | 2pm - 8pm (2 slots) | Male Only |
| ANC | 7am - 11am | Female Only |
| ANC | 4pm - 8pm | Female Only |
| WIC | 5pm - 11pm (2 slots) | Any Gender |
| TRIAGE | 7am - 2pm | Any Gender |

### Additional Shifts (For Remaining Staff)
| Shift | Time | Gender Requirement |
|-------|------|-------------------|
| FMC | 7am - 2pm | Any Gender |
| FMC | 4pm - 10pm | Any Gender |
| WIC | 7am - 2pm | Any Gender |
| WIC | 4pm - 10pm | Any Gender |

## Weekly Shift Pattern
```
Two Week Rotation:
Week 1          Team 1    Team 2
Sunday          AM        PM
Monday          AM        PM
Tuesday         AM        PM
Wednesday       PM        AM
Thursday        PM        AM

Week 2          Team 1    Team 2
Sunday          PM        AM
Monday          PM        AM
Tuesday         PM        AM
Wednesday       AM        PM
Thursday        AM        PM
```

## Shift Availability Matrix
| Day | WBC AM | WBC PM | TRIAGE 9-4 | TRIAGE 2-8 | TRIAGE 2-8 | ANC AM | ANC PM | FMC AM | FMC PM | WIC AM | WIC PM | WIC 5-11 | WIC 5-11 | TRIAGE 7-2 |
|-----|---------|---------|------------|------------|------------|---------|---------|---------|---------|---------|---------|-----------|-----------|------------|
| Sun | No | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Mon | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Tue | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Wed | Yes | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Thu | No | No | Yes | Yes | Yes | No | No | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

## Shift Preferences and Constraints

1. Special Shift Considerations:
   - Thursday 2pm-8pm is preferred when team is on PM rotation (earlier finish before weekend)
   - 5pm-11pm shifts require high-priority equal distribution
   - Tuesday 5pm-11pm should be followed by Wednesday 2pm-8pm or 9am-4pm
   - Maximum one 2pm-8pm shift per 5-day AM/PM run

2. Priority Order:
   - Fill essential shifts first
   - Maintain gender requirements
   - Allocate remaining staff to FMC/WIC shifts
   - Flag discrepancies of >2 doctors per day

2. Constraints:
   - One shift per doctor per day
   - Middle shift (2pm-8pm) requires one doctor from each team
   - Annual Leave (AL) handling prioritizes shift coverage over team balance

3. Monitoring Requirements:
   - Track shift distribution equity
   - Alert on >2 doctor discrepancies
   - Monitor AL impact on distribution
   - Ensure gender requirement compliance

## System Outputs
1. Daily schedule showing:
   - All shift assignments
   - Team balance
   - Gender requirement compliance
   - Discrepancy flags
2. Distribution reports:
   - Shift equity per doctor
   - AL impact analysis
   - Team balance metrics