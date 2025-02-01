from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import logging

from ..interfaces.shift_interfaces import Schedule, Shift
from .shift_allocator import ShiftAllocator
from .rotation_pattern import RotationPattern
from .equity_tracker import EquityTracker
from .optimization_metrics import OptimizationMetrics, OptimizationResult, OptimizationHistory
from .optimization_strategies import (
    PriorityBasedStrategy,
    EquityBasedStrategy,
    PreferenceBasedStrategy,
    TeamBalanceStrategy,
    AggressiveOptimizationStrategy,
    ConflictResolutionStrategy
)
from ..services.conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)

class RotationEngine:
    """Core engine for generating and optimizing rotation schedules"""
    
    def __init__(self, shift_allocator: ShiftAllocator, pattern: RotationPattern):
        self.shift_allocator = shift_allocator
        self.pattern = pattern
        self.equity_tracker = EquityTracker()
        self.conflict_resolver = ConflictResolver(self.shift_allocator.staff_loader)
        
        # Initialize optimization strategies
        self.strategies = [
            PriorityBasedStrategy(shift_allocator, self.equity_tracker),
            EquityBasedStrategy(shift_allocator, self.equity_tracker),
            PreferenceBasedStrategy(shift_allocator),
            TeamBalanceStrategy(shift_allocator),
            ConflictResolutionStrategy(shift_allocator, self.conflict_resolver),
            AggressiveOptimizationStrategy(
                shift_allocator,
                self.equity_tracker,
                self.shift_allocator.validator
            )
        ]
        
        # Initialize optimization history
        self.optimization_history = OptimizationHistory([])
    
    def generate_schedule(self, start_date: datetime, end_date: datetime) -> Schedule:
        """Generate a schedule for the specified date range"""
        schedule = Schedule()
        current_date = start_date
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Get shifts for current day
            daily_shifts = self.shift_allocator.allocate_shifts(current_date)
            
            # Add shifts to schedule
            for shift in daily_shifts:
                schedule.add_shift(shift)
            
            current_date += timedelta(days=1)
        
        # Optimize the initial schedule
        return self.optimize_schedule(schedule)
    
    def optimize_schedule(self, schedule: Schedule, max_iterations: int = 5) -> Schedule:
        """Optimize a schedule using multiple strategies"""
        best_schedule = schedule
        best_metrics = OptimizationMetrics.calculate_from_schedule(
            schedule,
            self.equity_tracker,
            self.shift_allocator.validator
        )
        
        # Check for initial conflicts
        initial_conflicts = self.conflict_resolver.detect_conflicts(schedule)
        if initial_conflicts:
            logger.info(f"Initial schedule has {len(initial_conflicts)} conflicts")
        
        # Record initial state
        initial_result = OptimizationResult(
            schedule=schedule,
            metrics=best_metrics,
            strategy="initial",
            iteration=0
        )
        
        self.optimization_history.add_result(initial_result)
        
        for iteration in range(max_iterations):
            logger.info(f"Starting optimization iteration {iteration + 1}")
            
            # Try each optimization strategy
            for strategy in self.strategies:
                logger.info(f"Applying {strategy.get_name()} strategy")
                
                # Apply strategy
                candidate = strategy.optimize(best_schedule)
                
                # Check for conflicts after optimization
                conflicts = self.conflict_resolver.detect_conflicts(candidate)
                if conflicts:
                    logger.info(f"Found {len(conflicts)} conflicts after {strategy.get_name()} strategy")
                    continue  # Skip this candidate if it has conflicts
                
                # Evaluate candidate
                metrics = OptimizationMetrics.calculate_from_schedule(
                    candidate,
                    self.equity_tracker,
                    self.shift_allocator.validator
                )
                
                # Record result
                result = OptimizationResult(
                    schedule=candidate,
                    metrics=metrics,
                    strategy=strategy.get_name(),
                    iteration=iteration + 1
                )
                self.optimization_history.add_result(result)
                
                # Update best if improved and no conflicts
                if metrics.total_score > best_metrics.total_score:
                    improvement = (metrics.total_score - best_metrics.total_score) / abs(best_metrics.total_score)
                    logger.info(f"Found better schedule using {strategy.get_name()} "
                              f"(improvement: {improvement:.2%})")
                    best_schedule = candidate
                    best_metrics = metrics
            
            # Early stopping if no improvement
            if best_schedule == schedule:
                logger.info("No improvement in this iteration, stopping early")
                break
            
            schedule = best_schedule
        
        # Final conflict check
        final_conflicts = self.conflict_resolver.detect_conflicts(best_schedule)
        if final_conflicts:
            logger.warning(f"Final schedule has {len(final_conflicts)} unresolved conflicts")
        
        return best_schedule
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get metrics about the optimization process"""
        if not self.optimization_history.results:
            return {}
        
        return {
            'improvement_trend': self.optimization_history.get_improvement_trend(),
            'strategy_performance': self.optimization_history.get_strategy_performance(),
            'best_score': self.optimization_history.best_result.metrics.total_score if self.optimization_history.best_result else None,
            'iterations': len(set(r.iteration for r in self.optimization_history.results)),
            'strategies_used': list(set(r.strategy for r in self.optimization_history.results))
        } 