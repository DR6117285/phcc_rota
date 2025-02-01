# Medical Rota System Documentation

## System Overview
The Medical Rota System is a comprehensive solution for managing medical staff scheduling, ensuring fair distribution of shifts while maintaining compliance with various constraints including gender requirements, team balance, and staff preferences.

## Documentation Sections
1. [System Architecture](architecture.md)
2. [API Documentation](api/README.md)
3. [User Guide](user_guide/README.md)
4. [Deployment Guide](deployment/README.md)
5. [Testing Guide](testing/README.md)

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest src/tests/

# Generate sample schedule
python src/main.py generate-schedule --start-date 2024-01-01 --days 7
```

## Key Features
- Automated shift allocation with constraint satisfaction
- Gender requirement compliance
- Team balance optimization
- Staff preference consideration
- Equity tracking across allocations
- Detailed Excel reports with visualizations
- Performance optimization (<5 seconds for weekly allocation)

## System Requirements
- Python 3.11+
- Required packages listed in requirements.txt
- Excel for report viewing

## Support
For issues and feature requests, please use the issue tracker in the repository. 