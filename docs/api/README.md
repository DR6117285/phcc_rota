# Medical Rota System API Documentation

## Overview

The Medical Rota System provides a comprehensive API for schedule generation, optimization, and conflict resolution. This document outlines the main components and their interfaces.

## Core Components

### 1. RotationEngine

The `RotationEngine` is the main entry point for schedule generation and optimization.

```python
class RotationEngine:
    def __init__(self, shift_allocator: ShiftAllocator, pattern: RotationPattern):
        """Initialize the rotation engine
        
        Args:
            shift_allocator: Component for allocating shifts to staff
            pattern: The rotation pattern to follow
        """
        pass

    def generate_schedule(self, start_date: datetime, end_date: datetime) -> Schedule:
        """Generate a schedule for the specified date range
        
        Args:
            start_date: Start date for the schedule
            end_date: End date for the schedule
            
        Returns:
            A Schedule object containing all allocated shifts
        """
        pass

    def optimize_schedule(self, schedule: Schedule, max_iterations: int = 5) -> Schedule:
        """Optimize a schedule using multiple strategies
        
        Args:
            schedule: The schedule to optimize
            max_iterations: Maximum number of optimization iterations
            
        Returns:
            An optimized Schedule object
        """
        pass

    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get metrics about the optimization process
        
        Returns:
            Dictionary containing:
            - improvement_trend: List of scores showing optimization progress
            - strategy_performance: Performance metrics for each strategy
            - best_score: Best optimization score achieved
            - iterations: Number of iterations performed
            - strategies_used: List of strategies applied
        """
        pass
```

### 2. ConflictResolver

The `ConflictResolver` handles detection and resolution of schedule conflicts.

```python
class ConflictResolver:
    def detect_conflicts(self, schedule: Dict[str, Any]) -> List[Conflict]:
        """Detect all conflicts in the schedule
        
        Args:
            schedule: The schedule to check for conflicts
            
        Returns:
            List of detected conflicts
        """
        pass

    def suggest_resolutions(self, conflict: Conflict) -> List[Dict[str, Any]]:
        """Suggest possible resolutions for a conflict
        
        Args:
            conflict: The conflict to resolve
            
        Returns:
            List of possible resolutions with their details
        """
        pass

    def apply_resolution(self, conflict: Conflict, resolution: Dict[str, Any]) -> bool:
        """Apply a selected resolution to the schedule
        
        Args:
            conflict: The conflict to resolve
            resolution: The chosen resolution to apply
            
        Returns:
            True if resolution was successfully applied
        """
        pass

    def get_distribution_metrics(self, 
                               schedule: Dict[str, Any],
                               start_date: date,
                               end_date: date) -> Dict[str, Any]:
        """Get shift distribution metrics for a date range
        
        Args:
            schedule: The schedule to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing distribution metrics
        """
        pass
```

### 3. Optimization Strategies

The system provides several optimization strategies:

#### PriorityBasedStrategy
Optimizes schedule prioritizing essential shifts.

```python
class PriorityBasedStrategy(OptimizationStrategy):
    def optimize(self, schedule: Schedule) -> Schedule:
        """Optimize based on shift priorities"""
        pass
```

#### EquityBasedStrategy
Optimizes for workload equity among staff.

```python
class EquityBasedStrategy(OptimizationStrategy):
    def optimize(self, schedule: Schedule) -> Schedule:
        """Optimize for equitable workload distribution"""
        pass
```

#### PreferenceBasedStrategy
Optimizes based on staff preferences.

```python
class PreferenceBasedStrategy(OptimizationStrategy):
    def optimize(self, schedule: Schedule) -> Schedule:
        """Optimize based on staff preferences"""
        pass
```

#### TeamBalanceStrategy
Optimizes for balanced team assignments.

```python
class TeamBalanceStrategy(OptimizationStrategy):
    def optimize(self, schedule: Schedule) -> Schedule:
        """Optimize for team balance"""
        pass
```

#### AggressiveOptimizationStrategy
Applies multiple optimization techniques aggressively.

```python
class AggressiveOptimizationStrategy(OptimizationStrategy):
    def optimize(self, schedule: Schedule) -> Schedule:
        """Aggressively optimize using multiple techniques"""
        pass
```

## Data Models

### Schedule
```python
@dataclass
class Schedule:
    shifts: List[Shift]
    
    def add_shift(self, shift: Shift):
        """Add a shift to the schedule"""
        pass
    
    def get_all_shifts(self) -> List[Shift]:
        """Get all shifts in the schedule"""
        pass
```

### Shift
```python
@dataclass
class Shift:
    id: str
    shift_definition: ShiftDefinition
    date: date
    assigned_doctor_id: Optional[str]
```

### Conflict
```python
@dataclass
class Conflict:
    conflict_type: ConflictType
    severity: ConflictSeverity
    description: str
    affected_shifts: List[Dict[str, Any]]
    affected_staff: List[str]
    possible_resolutions: List[Dict[str, Any]]
    metrics: Dict[str, Any]
```

## Usage Examples

### 1. Generate and Optimize Schedule

```python
# Initialize components
shift_allocator = ShiftAllocator(validator, equity_tracker, staff_loader)
pattern = RotationPattern(start_date)
engine = RotationEngine(shift_allocator, pattern)

# Generate schedule
schedule = engine.generate_schedule(start_date, end_date)

# Optimize schedule
optimized_schedule = engine.optimize_schedule(schedule)

# Get optimization metrics
metrics = engine.get_optimization_metrics()
```

### 2. Handle Conflicts

```python
# Initialize resolver
resolver = ConflictResolver(staff_loader)

# Detect conflicts
conflicts = resolver.detect_conflicts(schedule)

# Handle each conflict
for conflict in conflicts:
    # Get resolution suggestions
    resolutions = resolver.suggest_resolutions(conflict)
    
    # Apply first valid resolution
    for resolution in resolutions:
        if resolver.apply_resolution(conflict, resolution):
            break
```

### 3. Get Distribution Metrics

```python
# Get metrics for a date range
metrics = resolver.get_distribution_metrics(
    schedule,
    start_date,
    end_date
)

# Access specific metrics
shift_counts = metrics['shift_counts']
team_distribution = metrics['team_distribution']
workload_metrics = metrics['workload_metrics']
```

## Configuration Options

### Optimization Parameters
- `max_iterations`: Maximum optimization iterations (default: 5)
- `improvement_threshold`: Minimum improvement to continue (default: 0.01)

### Conflict Resolution Parameters
- `min_rest_period`: Minimum hours between shifts (default: 8)
- `max_workload_difference`: Maximum workload difference allowed (default: 4)
- `team_balance_threshold`: Maximum team assignment difference (default: 2)

### Performance Settings
- `optimization_timeout`: Maximum seconds for optimization (default: 5)
- `resolution_timeout`: Maximum seconds for conflict resolution (default: 2)

## Error Handling

The system uses a comprehensive error handling approach:

1. **ValidationError**: Raised for invalid schedule configurations
2. **ConflictError**: Raised for unresolvable conflicts
3. **OptimizationError**: Raised for optimization failures
4. **TimeoutError**: Raised when operations exceed time limits

Example error handling:

```python
try:
    schedule = engine.generate_schedule(start_date, end_date)
except ValidationError as e:
    logger.error(f"Invalid schedule configuration: {e}")
except OptimizationError as e:
    logger.error(f"Optimization failed: {e}")
except TimeoutError as e:
    logger.error(f"Operation timed out: {e}")
``` 