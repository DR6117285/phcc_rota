# Deployment Guide

## System Requirements

### Hardware Requirements
- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- Storage: 1GB for application and data

### Software Requirements
- Python 3.11+
- Microsoft Excel (for report viewing)
- Git (for version control)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-org/medical-rota.git
cd medical-rota
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rota_db
DB_USER=rota_user
DB_PASSWORD=your_secure_password

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
REPORT_OUTPUT_DIR=/path/to/reports
```

### 5. Database Setup
```bash
# Initialize database
python scripts/init_db.py

# Run migrations
python scripts/migrate_db.py
```

### 6. Test Installation
```bash
# Run test suite
python -m pytest

# Generate test schedule
python src/main.py generate-schedule --start-date 2024-01-01 --days 7
```

## Production Deployment

### 1. Security Considerations
- Use HTTPS for all connections
- Set up proper firewall rules
- Configure secure database access
- Implement backup strategy
- Set up monitoring

### 2. Performance Tuning
```python
# config/production.py
CACHE_ENABLED = True
CACHE_TIMEOUT = 3600
BATCH_SIZE = 1000
MAX_WORKERS = 4
```

### 3. Logging Configuration
```python
# config/logging.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/rota.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'rota': {
            'handlers': ['file'],
            'level': 'INFO'
        }
    }
}
```

### 4. Backup Strategy
```bash
# Backup script (backup.sh)
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups"

# Backup database
pg_dump rota_db > "$BACKUP_DIR/db_$DATE.sql"

# Backup configuration
cp .env "$BACKUP_DIR/env_$DATE"

# Backup reports
tar -czf "$BACKUP_DIR/reports_$DATE.tar.gz" /path/to/reports/
```

### 5. Monitoring Setup
- Set up health checks
- Configure error alerting
- Monitor system metrics
- Track performance indicators

## Scaling Considerations

### 1. Horizontal Scaling
- Load balancer configuration
- Session management
- Database replication
- Caching strategy

### 2. Vertical Scaling
- CPU optimization
- Memory management
- Disk I/O optimization
- Database tuning

### 3. Performance Monitoring
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram

schedule_generation_time = Histogram(
    'schedule_generation_seconds',
    'Time spent generating schedules'
)

constraint_violations = Counter(
    'constraint_violations_total',
    'Number of constraint violations'
)
```

## Troubleshooting

### Common Issues

1. Database Connection
```bash
# Check database status
python scripts/check_db.py

# Reset database connection
python scripts/reset_db_connection.py
```

2. Report Generation
```bash
# Verify Excel installation
python scripts/check_excel.py

# Clear report cache
python scripts/clear_report_cache.py
```

3. Performance Issues
```bash
# Run performance diagnostics
python scripts/diagnose_performance.py

# Clear system cache
python scripts/clear_cache.py
```

### Error Recovery

1. Backup Restoration
```bash
# Restore database
python scripts/restore_db.py --backup-file backup.sql

# Restore configuration
python scripts/restore_config.py --backup-file config.bak
```

2. System Reset
```bash
# Reset to clean state
python scripts/reset_system.py

# Rebuild indexes
python scripts/rebuild_indexes.py
```

## Maintenance

### Regular Tasks
1. Database maintenance
2. Log rotation
3. Backup verification
4. Performance monitoring
5. Security updates

### Update Procedure
```bash
# Update application
git pull origin main
pip install -r requirements.txt
python scripts/migrate_db.py
python scripts/clear_cache.py
systemctl restart rota-service
``` 