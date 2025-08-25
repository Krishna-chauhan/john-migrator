# Example configuration file for john-migrator
# Copy this file to your project root and rename it to 'john_migrator_config.py'
# Then modify the values according to your database setup

# Database Configuration
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "your_database"

# Migration Configuration (optional)
MIGRATION_FOLDER = "migrations"  # Default: ./migrations
MIGRATION_TABLE = "migrations"   # Default: migrations

# ORM Model Configuration (optional)
MODELS_FOLDER = "models"  # Default: ./models
GENERATE_ORM_MODELS = True  # Set to False to disable ORM model generation
ORM_BASE_CLASS = "Base"  # SQLAlchemy base class name

# Example for different database types:
# PostgreSQL (default)
# DATABASE_URL = "postgresql://user:pass@localhost:5432/dbname"

# MySQL
# DATABASE_URL = "mysql://user:pass@localhost:3306/dbname"
# Note: For MySQL, you'll need to install mysqlclient or pymysql
