from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class OptimizationMetrics:
    """Metrics for evaluating schedule quality"""
    unassigned_shifts: int
    equity_score: float
    team_balance_score: float
    preference_satisfaction: float
    constraint_violations: int
    total_score: float

    @classmethod
    def calculate_from_schedule(cls, schedule, equity_tracker, shift_validator) -> 'OptimizationMetrics':
        """Calculate metrics from a schedule"""
        # Count unassigned shifts
        unassigned = len([s for s in schedule.get_all_shifts() if not s.assigned_doctor_id])
        
        # Get equity score from tracker
        equity_score = equity_tracker.calculate_equity_score(schedule)
        
        # Calculate team balance
        team_stats = {'A': 0, 'B': 0}
        for shift in schedule.get_all_shifts():
            if shift.assigned_doctor_id:
                doctor = shift_validator.staff_loader.get_doctor_by_id(shift.assigned_doctor_id)
                team_stats[doctor.team] += 1
        total_shifts = sum(team_stats.values())
        team_balance_score = 1.0 - (abs(team_stats['A'] - team_stats['B']) / total_shifts if total_shifts > 0 else 0)
        
        # Calculate preference satisfaction
        total_preferences = 0
        satisfied_preferences = 0
        for shift in schedule.get_all_shifts():
            if shift.assigned_doctor_id:
                doctor = shift_validator.staff_loader.get_doctor_by_id(shift.assigned_doctor_id)
                if doctor.preferences:
                    total_preferences += 1
                    if shift.shift_definition.shift_type in doctor.preferences:
                        satisfied_preferences += 1
        preference_satisfaction = satisfied_preferences / total_preferences if total_preferences > 0 else 1.0
        
        # Count constraint violations
        violations = shift_validator.validate_schedule(schedule)
        constraint_violations = len(violations)
        
        # Calculate total score (weighted sum of all metrics)
        total_score = (
            -5.0 * unassigned +  # Heavy penalty for unassigned shifts
            3.0 * equity_score +  # High importance for equity
            2.0 * team_balance_score +  # Medium importance for team balance
            1.0 * preference_satisfaction +  # Lower importance for preferences
            -4.0 * constraint_violations  # Heavy penalty for violations
        )
        
        return cls(
            unassigned_shifts=unassigned,
            equity_score=equity_score,
            team_balance_score=team_balance_score,
            preference_satisfaction=preference_satisfaction,
            constraint_violations=constraint_violations,
            total_score=total_score
        )

@dataclass
class OptimizationResult:
    """Result of an optimization attempt"""
    schedule: 'Schedule'  # Forward reference
    metrics: OptimizationMetrics
    strategy: str
    iteration: int
    timestamp: datetime = datetime.now()
    
    def is_better_than(self, other: 'OptimizationResult') -> bool:
        """Compare if this result is better than another"""
        return self.metrics.total_score > other.metrics.total_score

@dataclass
class OptimizationHistory:
    """History of optimization attempts"""
    results: List[OptimizationResult]
    best_result: Optional[OptimizationResult] = None
    
    def add_result(self, result: OptimizationResult) -> None:
        """Add a new optimization result"""
        self.results.append(result)
        if not self.best_result or result.is_better_than(self.best_result):
            self.best_result = result
    
    def get_improvement_trend(self) -> List[float]:
        """Get list of scores showing improvement trend"""
        return [r.metrics.total_score for r in self.results]
    
    def get_strategy_performance(self) -> Dict[str, float]:
        """Get average improvement by strategy"""
        strategy_scores = {}
        strategy_counts = {}
        
        for result in self.results:
            if result.strategy not in strategy_scores:
                strategy_scores[result.strategy] = 0
                strategy_counts[result.strategy] = 0
            strategy_scores[result.strategy] += result.metrics.total_score
            strategy_counts[result.strategy] += 1
        
        return {
            strategy: scores / strategy_counts[strategy]
            for strategy, scores in strategy_scores.items()
        } 