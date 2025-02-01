# Medical Rota System User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [System Overview](#system-overview)
4. [Basic Operations](#basic-operations)
5. [Advanced Features](#advanced-features)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Introduction

The Medical Rota System is a comprehensive solution for managing medical staff schedules. It provides automated schedule generation, optimization, and conflict resolution capabilities while ensuring fair workload distribution and staff preferences consideration.

### Key Features
- Automated schedule generation
- Multiple optimization strategies
- Conflict detection and resolution
- Workload equity tracking
- Staff preference management
- Performance monitoring
- Comprehensive reporting

## Getting Started

### System Requirements
- Python 3.8 or higher
- Required packages (see requirements.txt)
- Minimum 4GB RAM
- 2GB free disk space

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/medical-rota-system.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the system:
   ```bash
   cp config.example.yml config.yml
   # Edit config.yml with your settings
   ```

4. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

## System Overview

### Core Components

1. **Schedule Generator**
   - Creates initial schedules
   - Handles basic shift allocation
   - Applies rotation patterns

2. **Optimization Engine**
   - Multiple optimization strategies
   - Performance metrics tracking
   - Iterative improvement

3. **Conflict Resolver**
   - Conflict detection
   - Resolution suggestions
   - Impact analysis

4. **Reporting System**
   - Schedule reports
   - Performance metrics
   - Distribution analysis

## Basic Operations

### 1. Generating a Schedule

```python
from medical_rota import RotationEngine

# Initialize the engine
engine = RotationEngine()

# Generate a schedule
schedule = engine.generate_schedule(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### 2. Managing Staff

```python
from medical_rota import StaffManager

# Add new staff
staff_manager.add_staff(
    name="Dr. Smith",
    team="A",
    gender="F",
    specialties=["emergency", "general"]
)

# Set leave dates
staff_manager.set_leave(
    staff_id="123",
    dates=["2024-01-15", "2024-01-16"]
)
```

### 3. Handling Conflicts

```python
from medical_rota import ConflictResolver

# Check for conflicts
conflicts = resolver.detect_conflicts(schedule)

# Resolve conflicts
for conflict in conflicts:
    resolutions = resolver.suggest_resolutions(conflict)
    resolver.apply_resolution(conflict, resolutions[0])
```

## Advanced Features

### 1. Custom Optimization Strategies

You can implement custom optimization strategies by extending the `OptimizationStrategy` class:

```python
class CustomStrategy(OptimizationStrategy):
    def optimize(self, schedule):
        # Your optimization logic here
        return optimized_schedule
```

### 2. Advanced Conflict Resolution

The system supports complex conflict resolution scenarios:

```python
# Analyze conflict impact
impact = resolver.analyze_impact(conflict)

# Get detailed metrics
metrics = resolver.get_distribution_metrics(
    schedule,
    start_date,
    end_date
)
```

### 3. Performance Monitoring

Monitor system performance:

```python
# Get optimization metrics
metrics = engine.get_optimization_metrics()

# Track resolution success rate
stats = resolver.get_resolution_stats()
```

## Configuration

### Basic Configuration
Edit `config.yml`:

```yaml
system:
  optimization:
    max_iterations: 5
    improvement_threshold: 0.01
  
  conflict_resolution:
    min_rest_period: 8  # hours
    max_workload_difference: 4
    
  performance:
    optimization_timeout: 5  # seconds
    resolution_timeout: 2  # seconds
```

### Advanced Configuration

#### Optimization Weights
```yaml
optimization_weights:
  priority: 3.0
  equity: 2.0
  preference: 1.5
  team_balance: 1.0
```

#### Constraint Settings
```yaml
constraints:
  consecutive_shifts:
    enabled: true
    min_rest_hours: 8
  
  workload_balance:
    enabled: true
    max_difference: 4
    
  team_balance:
    enabled: true
    max_difference: 2
```

## Troubleshooting

### Common Issues

1. **Schedule Generation Fails**
   - Check staff availability
   - Verify constraint settings
   - Review error logs

2. **Optimization Performance**
   - Reduce max_iterations
   - Adjust improvement_threshold
   - Check system resources

3. **Conflict Resolution Issues**
   - Review conflict types
   - Check resolution strategies
   - Verify staff data

### Error Messages

1. **ValidationError**
   ```
   Invalid schedule configuration: Constraint violation
   ```
   - Check constraint settings
   - Verify staff availability

2. **OptimizationError**
   ```
   Optimization failed: Maximum iterations reached
   ```
   - Adjust optimization parameters
   - Check performance settings

3. **TimeoutError**
   ```
   Operation timed out: Optimization exceeded time limit
   ```
   - Increase timeout settings
   - Reduce problem size

### Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Performance Tips

1. **Optimization**
   - Use appropriate max_iterations
   - Set reasonable improvement_threshold
   - Monitor system resources

2. **Conflict Resolution**
   - Handle conflicts in batches
   - Use appropriate timeout settings
   - Cache frequent operations

3. **General Performance**
   - Regular database maintenance
   - Monitor memory usage
   - Profile slow operations

### Getting Help

1. Check the [API Documentation](api/README.md)
2. Review error logs
3. Contact system administrator
4. Submit bug reports with:
   - Error messages
   - System configuration
   - Relevant logs 