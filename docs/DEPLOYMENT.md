# Deployment Guide - Ricoh Fleet Governance API

## 🚀 Production Deployment Options

### Option 1: Traditional Server (Ubuntu/Debian)

#### 1. Install Dependencies
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx supervisor
```

#### 2. Setup Application
```bash
# Clone repository
git clone <your-repo>
cd ricoh-suite/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

#### 3. Configure Supervisor
Create `/etc/supervisor/conf.d/ricoh-api.conf`:

```ini
[program:ricoh-api]
directory=/path/to/ricoh-suite/backend
command=/path/to/ricoh-suite/backend/venv/bin/python main.py
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ricoh-api.err.log
stdout_logfile=/var/log/ricoh-api.out.log
environment=DEMO_MODE="false"
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ricoh-api
```

#### 4. Configure Nginx
Create `/etc/nginx/sites-available/ricoh-api`:

```nginx
server {
    listen 80;
    server_name api.ricoh-fleet.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ricoh-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Docker

#### Build and Run
```bash
cd backend
docker build -t ricoh-fleet-api .
docker run -d -p 8000:8000 --name ricoh-api ricoh-fleet-api
```

#### Using Docker Compose
```bash
# From project root
docker-compose up -d
```

### Option 3: Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI
heroku login
heroku create ricoh-fleet-api

# Add Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku main
```

#### AWS EC2
1. Launch Ubuntu EC2 instance
2. Follow "Traditional Server" steps
3. Configure security group to allow port 8000
4. Use Elastic IP for static address

#### Google Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/ricoh-api

# Deploy
gcloud run deploy ricoh-api \
  --image gcr.io/PROJECT_ID/ricoh-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔒 Production Checklist

### Security
- [ ] Set `DEMO_MODE=false`
- [ ] Configure specific CORS origins (not `*`)
- [ ] Add authentication (JWT/OAuth)
- [ ] Use HTTPS/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Implement API key authentication
- [ ] Add request logging
- [ ] Set up monitoring/alerting

### Performance
- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Configure worker processes
- [ ] Set up load balancer
- [ ] Enable caching (Redis)
- [ ] Optimize database queries
- [ ] Add CDN for static assets

### Reliability
- [ ] Set up health checks
- [ ] Configure auto-restart
- [ ] Implement backup strategy
- [ ] Set up log rotation
- [ ] Monitor disk space
- [ ] Configure alerts

### Database
- [ ] Migrate from JSON to PostgreSQL/MongoDB
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Add database migrations (Alembic)

## 🔧 Production Configuration

### Environment Variables
```env
# Production settings
DEMO_MODE=false
API_HOST=0.0.0.0
API_PORT=8000

# CORS (specific origins)
CORS_ORIGINS=https://fleet.company.com,https://app.company.com

# Database (future)
DATABASE_URL=postgresql://user:pass@localhost/ricoh_fleet

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### Gunicorn Configuration
Create `gunicorn.conf.py`:

```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
errorlog = "/var/log/ricoh-api/error.log"
accesslog = "/var/log/ricoh-api/access.log"
loglevel = "info"
```

Run with:
```bash
gunicorn -c gunicorn.conf.py main:app
```

## 📊 Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8000/
```

### Prometheus Metrics (Future Enhancement)
Add to `main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Log Aggregation
Use ELK Stack, Datadog, or CloudWatch for centralized logging.

## 🔄 CI/CD Pipeline

### GitHub Actions Example
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          python test_api.py
      
      - name: Deploy to server
        run: |
          # Your deployment script here
```

## 🆘 Troubleshooting

### High Memory Usage
- Reduce worker count
- Implement connection pooling
- Add memory limits in Docker

### Slow Response Times
- Enable caching
- Optimize network scanning
- Add database indexes
- Use async operations

### Connection Timeouts
- Increase timeout values
- Check firewall rules
- Verify network connectivity

## 📞 Support

For production issues:
1. Check logs: `/var/log/ricoh-api/`
2. Verify service status: `supervisorctl status ricoh-api`
3. Test endpoints: `curl http://localhost:8000/`
4. Review error logs in application

## 🔄 Updates

### Rolling Updates
```bash
# Pull latest code
git pull origin main

# Restart service
sudo supervisorctl restart ricoh-api
```

### Zero-Downtime Deployment
Use blue-green deployment or rolling updates with load balancer.

## 📝 Backup Strategy

### Database Backup
```bash
# PostgreSQL
pg_dump ricoh_fleet > backup_$(date +%Y%m%d).sql

# MongoDB
mongodump --db ricoh_fleet --out backup_$(date +%Y%m%d)
```

### Configuration Backup
```bash
tar -czf config_backup_$(date +%Y%m%d).tar.gz backend/.env backend/fleet.json
```

## 🎯 Performance Tuning

### Uvicorn Workers
```bash
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Connection Pooling
Add to `main.py`:
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0
)
```

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use shared database
- Implement session management (Redis)

### Vertical Scaling
- Increase server resources (CPU/RAM)
- Optimize worker count
- Tune database performance
