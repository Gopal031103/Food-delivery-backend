# Deployment Guide

Complete guide for deploying the Food Delivery Management System to production.

## Pre-Deployment Checklist

### Security
- [ ] Change `SECRET_KEY` in .env to a strong random 32+ character string
- [ ] Set `DEBUG=False` in .env
- [ ] Disable CORS wildcard and specify allowed origins
- [ ] Configure HTTPS/SSL certificates
- [ ] Set strong MySQL root password
- [ ] Create dedicated database user with limited privileges
- [ ] Review and audit all environment variables
- [ ] Enable rate limiting
- [ ] Set up request logging and monitoring

### Performance
- [ ] Enable database connection pooling
- [ ] Configure caching strategy
- [ ] Set up CDN for static files
- [ ] Configure database indexes
- [ ] Load test the application
- [ ] Set up monitoring and alerting

### Infrastructure
- [ ] Set up monitoring (Prometheus, DataDog, etc.)
- [ ] Configure log aggregation (ELK, Splunk, etc.)
- [ ] Set up backup strategy
- [ ] Configure auto-scaling rules
- [ ] Set up health checks
- [ ] Create runbooks for common issues

## Deployment Options

### Option 1: AWS Deployment

#### Using EC2 + RDS

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# - Instance type: t3.medium or larger
# - Storage: 30GB gp3
# - Security group: Allow ports 80, 443, 3306 (internal only)

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install dependencies
sudo apt-get update
sudo apt-get install -y python3.13 python3-pip python3-venv mysql-client nginx supervisor

# 4. Clone repository
git clone your-repo-url
cd food_delivery

# 5. Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# 6. Install packages
pip install -r requirements.txt

# 7. Configure .env with RDS endpoint
# DATABASE_URL=mysql+mysqlconnector://user:pass@rds-endpoint:3306/food_delivery

# 8. Create RDS MySQL instance
# - Engine: MySQL 8.0
# - Instance class: db.t3.micro or larger
# - Storage: 20GB gp2
# - Multi-AZ: Enable for production
# - Backup retention: 7 days

# 9. Configure Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/food-delivery
sudo ln -s /etc/nginx/sites-available/food-delivery /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 10. Configure Supervisor
sudo cp deployment/supervisor.conf /etc/supervisor/conf.d/food-delivery.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start food-delivery

# 11. Set up SSL with Let's Encrypt
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

#### Production Environment File

Create `.env.production`:
```env
DATABASE_URL=mysql+mysqlconnector://food_user:strong_pass@rds-endpoint:3306/food_delivery
SQLALCHEMY_DATABASE_URL=mysql+mysqlconnector://food_user:strong_pass@rds-endpoint:3306/food_delivery
SECRET_KEY=your-secure-random-key-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Food Delivery Management System
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Option 2: Docker with Kubernetes

#### Build Production Docker Image

```dockerfile
# Multi-stage build for smaller image size
FROM python:3.13-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY app/ ./app/

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Push to Docker Registry

```bash
# Build image
docker build -t food-delivery:1.0.0 .

# Tag for registry
docker tag food-delivery:1.0.0 your-registry/food-delivery:1.0.0

# Push to registry
docker push your-registry/food-delivery:1.0.0
```

#### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: food-delivery-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: food-delivery-api
  template:
    metadata:
      labels:
        app: food-delivery-api
    spec:
      containers:
      - name: api
        image: your-registry/food-delivery:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: food-delivery-api-service
spec:
  selector:
    app: food-delivery-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Option 3: Heroku Deployment

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create your-app-name

# 4. Add MySQL database addon
heroku addons:create cleardb:ignite

# 5. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ENVIRONMENT=production

# 6. Deploy
git push heroku main

# 7. View logs
heroku logs --tail
```

Create `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Option 4: DigitalOcean App Platform

```bash
# 1. Create app.yaml
cat > app.yaml << EOF
name: food-delivery-api
services:
- name: api
  github:
    repo: your-github-repo
    branch: main
  build_command: pip install -r requirements.txt
  run_command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  http_port: 8000
  envs:
  - key: DEBUG
    value: "False"
  - key: ENVIRONMENT
    value: production
  - key: SECRET_KEY
    value: ${SECRET_KEY}
databases:
- name: food_db
  engine: MYSQL
  version: "8.0"
  production: true
EOF

# 2. Deploy via DigitalOcean CLI
doctl apps create --spec app.yaml
```

## Post-Deployment

### Verify Deployment

```bash
# Check health endpoint
curl https://your-domain.com/health

# Check API documentation
curl https://your-domain.com/api/docs

# Run smoke tests
pytest tests/ -m smoke
```

### Monitoring Setup

#### CloudWatch (AWS)

```python
# Add to app/main.py
import watchtower
import logging

# Configure CloudWatch logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(watchtower.CloudWatchLogHandler())
```

#### Datadog

```python
from datadog import initialize, api

options = {
    'api_key': 'your-api-key',
    'app_key': 'your-app-key'
}

initialize(**options)

# Send custom metrics
api.Metric.send(
    metric='food_delivery.orders',
    points=value,
    tags=['env:production']
)
```

### Database Maintenance

```bash
# Connect to production database
mysql -u food_user -p -h your-db-host -D food_delivery

# Run backups
mysqldump -u food_user -p -h your-db-host food_delivery | gzip > backup_$(date +%Y%m%d).sql.gz

# Schedule automated backups (cron)
0 2 * * * mysqldump -u food_user -p -h db-host food_delivery | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### SSL/HTTPS Configuration

#### Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/limited")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "Limited endpoint"}
```

### Automated Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DB_HOST="your-db-host"
DB_USER="food_user"
DB_NAME="food_delivery"
RETENTION_DAYS=7

# Create backup
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Delete old backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully"
```

Add to crontab:
```
0 2 * * * /path/to/backup.sh
```

## Scaling Considerations

### Horizontal Scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: food-delivery-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: food-delivery-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Caching Strategy

```python
from functools import lru_cache
import redis

# Redis caching
redis_client = redis.Redis(host='cache-host', port=6379)

@app.get("/restaurants")
async def list_restaurants(skip: int = 0, limit: int = 10):
    cache_key = f"restaurants:{skip}:{limit}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query database
    restaurants = db.query(Restaurant).offset(skip).limit(limit).all()
    
    # Cache result for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(restaurants))
    
    return restaurants
```

## Rollback Procedure

```bash
# Docker rollback
docker pull your-registry/food-delivery:1.0.0-previous
docker stop current-container
docker run -d your-registry/food-delivery:1.0.0-previous

# Kubernetes rollback
kubectl rollout undo deployment/food-delivery-api
kubectl rollout status deployment/food-delivery-api

# Database rollback
mysql -u food_user -p -h db-host food_delivery < backup_file.sql
```

## Support & Monitoring

- Set up alerting for error rates > 1%
- Monitor response time P95 < 500ms
- Set up on-call rotation
- Document runbooks for common issues
- Regular disaster recovery drills

## Compliance & Security

- [ ] GDPR compliance (if applicable)
- [ ] PCI DSS compliance (for payment processing)
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] WAF (Web Application Firewall) rules
- [ ] API rate limiting
- [ ] Input validation and sanitization
