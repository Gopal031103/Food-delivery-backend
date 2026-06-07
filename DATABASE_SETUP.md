# Database Setup Guide

## MySQL Installation and Configuration

### Windows

1. Download MySQL installer from https://dev.mysql.com/downloads/installer/
2. Run the installer
3. Follow the setup wizard
4. Choose "MySQL Server" component
5. Configure MySQL as Windows Service
6. Note the port (default: 3306)
7. Set root password

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

### macOS (using Homebrew)

```bash
brew install mysql
mysql.server start
mysql_secure_installation
```

## Creating Database and User

### Using MySQL CLI

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE food_delivery;

-- Create user (optional, for security)
CREATE USER 'food_user'@'localhost' IDENTIFIED BY 'food_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON food_delivery.* TO 'food_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
EXIT;
```

### Using Docker

```bash
# Run MySQL container
docker run --name food_db \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=food_delivery \
  -p 3306:3306 \
  -d mysql:8.0

# Connect to container
docker exec -it food_db mysql -u root -p
```

## Verifying Database Connection

```python
# Python script to test connection
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+mysqlconnector://root:root@localhost:3306/food_delivery"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

## Database Schema Creation

The application automatically creates tables on startup if they don't exist.

To verify tables are created:

```sql
USE food_delivery;
SHOW TABLES;
DESCRIBE users;
DESCRIBE restaurants;
DESCRIBE menu_items;
DESCRIBE orders;
DESCRIBE order_items;
DESCRIBE payments;
```

## Backing Up Database

### Create Backup

```bash
mysqldump -u root -p food_delivery > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore from Backup

```bash
mysql -u root -p food_delivery < backup_file.sql
```

## Database Optimization

### Create Indexes

```sql
USE food_delivery;

-- Index for faster user lookup by email
CREATE INDEX idx_users_email ON users(email);

-- Index for faster restaurant lookup by city
CREATE INDEX idx_restaurants_city ON restaurants(city);

-- Index for faster order lookup by user
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Index for faster order items lookup
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

-- Show indexes
SHOW INDEXES FROM users;
```

## Troubleshooting

### Connection Refused

```bash
# Check MySQL service status
sudo service mysql status
sudo systemctl start mysql

# On macOS
mysql.server start
```

### Access Denied

```bash
# Reset MySQL root password (Linux)
sudo /etc/init.d/mysql stop
sudo mysqld_safe --skip-grant-tables &
mysql -u root

USE mysql;
UPDATE user SET authentication_string=PASSWORD('new_password') 
WHERE User='root';
FLUSH PRIVILEGES;
```

### Database Size

```sql
-- Check database size
SELECT 
  TABLE_SCHEMA AS 'Database', 
  ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS 'Size (MB)'
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'food_delivery'
GROUP BY TABLE_SCHEMA;
```

## Performance Monitoring

### Query Execution Time

```sql
-- Enable query execution time monitoring
SET SESSION sql_mode='STRICT_TRANS_TABLES';
SET GLOBAL log_queries_not_using_indexes=1;

-- Check slow query log
SHOW VARIABLES LIKE 'slow_query_log%';
```

### Database Statistics

```sql
-- Table statistics
SELECT 
  table_name,
  ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb,
  table_rows
FROM information_schema.tables
WHERE table_schema = 'food_delivery'
ORDER BY size_mb DESC;
```

## Migration Strategy

If you need to modify schema, you can use Alembic:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## User Account Management

### Add New User Programmatically

```python
from app.auth import PasswordManager
from app.database import SessionLocal
from app.models import User, UserRole

db = SessionLocal()

# Create admin user
admin_user = User(
    name="Admin User",
    email="admin@example.com",
    phone="9999999999",
    password_hash=PasswordManager.hash_password("AdminPass123!"),
    role=UserRole.ADMIN
)

db.add(admin_user)
db.commit()
```

## Regular Maintenance

### Weekly
- Check database size
- Review error logs
- Verify backups

### Monthly
- Optimize tables
- Update statistics
- Archive old logs

### Quarterly
- Performance analysis
- Capacity planning
- Security audit

## Security Considerations

1. **Disable Remote Root Login**
```sql
DELETE FROM mysql.user WHERE User='root' AND Host='%';
FLUSH PRIVILEGES;
```

2. **Create Strong Passwords**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, special characters

3. **Limit Privileges**
- Use specific database privileges
- Avoid using root for application

4. **Regular Backups**
- Automated daily backups
- Test restore procedures

5. **Monitor Access**
```sql
-- Enable audit logging
SET GLOBAL general_log = 'ON';
SET GLOBAL log_output = 'TABLE';
```
