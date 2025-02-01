# Medical Rota System

A comprehensive solution for managing medical staff schedules with automated optimization and conflict resolution.

## Features

- 🔄 Automated schedule generation
- ⚡ Multiple optimization strategies
- 🚫 Conflict detection and resolution
- ⚖️ Workload equity tracking
- 👥 Staff preference management
- 📊 Performance monitoring
- 📝 Comprehensive reporting

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/medical-rota-system.git
cd medical-rota-system
```

2. Create and activate virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the system:
```bash
cp config.example.yml config.yml
# Edit config.yml with your settings
```

5. Initialize the database:
```bash
python scripts/init_db.py
```

## Usage

### Basic Schedule Generation

```python
from medical_rota import RotationEngine

# Initialize the engine
engine = RotationEngine()

# Generate a schedule
schedule = engine.generate_schedule(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Optimize the schedule
optimized_schedule = engine.optimize_schedule(schedule)
```

### Managing Staff

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

### Handling Conflicts

```python
from medical_rota import ConflictResolver

# Check for conflicts
conflicts = resolver.detect_conflicts(schedule)

# Resolve conflicts
for conflict in conflicts:
    resolutions = resolver.suggest_resolutions(conflict)
    resolver.apply_resolution(conflict, resolutions[0])
```

## Documentation

- [User Guide](docs/user_guide.md) - Comprehensive guide for users
- [Technical Documentation](docs/technical_docs.md) - Detailed documentation for developers
- [API Documentation](docs/api/README.md) - API reference

## Configuration

The system can be configured through `config.yml`:

```yaml
system:
  optimization:
    max_iterations: 5
    improvement_threshold: 0.01
  
  conflict_resolution:
    min_rest_period: 8  # hours
    max_workload_difference: 4
```

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_optimization.py

# Run with coverage
pytest --cov=medical_rota tests/
```

### Code Style

This project follows PEP 8 guidelines. Use the provided pre-commit hooks to ensure code quality:

```bash
# Manual style check
flake8 medical_rota

# Format code
black medical_rota
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-org/medical-rota-system/issues)
- 💬 [Discussion Forum](https://github.com/your-org/medical-rota-system/discussions)

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the medical staff who provided valuable feedback
- Built with Python and modern software engineering practices

## Project Status

- ✅ Core functionality complete
- 🚧 Documentation in progress
- 🔄 Continuous improvements and optimizations
- 📈 Regular updates and maintenance

## Roadmap

- [ ] Enhanced optimization algorithms
- [ ] Machine learning integration
- [ ] Mobile application
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard

## Contact

- Project Maintainer: [Your Name](mailto:your.email@example.com)
- Organization: [Your Organization](https://your-org.com)

---

Made with ❤️ for medical professionals 