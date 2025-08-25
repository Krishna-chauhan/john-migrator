"""
Migration Manager for DB Migrator
Main orchestrator for migration operations
"""

import os
import sys
from typing import List

# Handle imports for both direct execution and package import
try:
    from .config import Config
    from .database_manager import DatabaseManager
    from .migration_generator import MigrationGenerator
    from .migration_runner import MigrationRunner
    from .orm_generator import ORMGenerator
    from .model_to_migration_generator import ModelToMigrationGenerator
except ImportError:
    # When running as script directly
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import Config
    from database_manager import DatabaseManager
    from migration_generator import MigrationGenerator
    from migration_runner import MigrationRunner
    from orm_generator import ORMGenerator
    from model_to_migration_generator import ModelToMigrationGenerator


class MigrationManager:
    """Main migration manager that orchestrates all migration operations"""
    
    def __init__(self):
        self.config = Config()
        self.db_manager = DatabaseManager()
        self.generator = MigrationGenerator()
        self.runner = MigrationRunner()
        self.orm_generator = ORMGenerator(self.config) if self.config.GENERATE_ORM_MODELS else None
        self.model_to_migration_generator = ModelToMigrationGenerator(self.config)
    
    def init_project(self):
        """Initialize the project with a default configuration file."""
        config_content = """# john_migrator_config.py
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
"""
        
        config_file = "john_migrator_config.py"
        
        if os.path.exists(config_file):
            print(f"⚠️  Configuration file '{config_file}' already exists.")
            response = input("Do you want to overwrite it? (y/N): ")
            if response.lower() != 'y':
                print("❌ Configuration file creation cancelled.")
                return
        
        with open(config_file, "w") as f:
            f.write(config_content)
        
        print(f"✅ Configuration file '{config_file}' created successfully!")
        print("📝 Please edit the file with your database credentials before running migrations.")
        print("💡 You can also use environment variables instead of editing this file.")
    
    def create_migration(self, migration_name, columns=None):
        """Create a new migration file."""
        if columns:
            print(f"📝 Creating migration '{migration_name}' with columns: {', '.join(columns)}")
        else:
            print(f"📝 Creating migration '{migration_name}' with default columns")
        
        self.generator.create_migration(migration_name, columns)
    
    def create_alter_migration(self, table_name, operations):
        """Create an ALTER TABLE migration file.
        
        Args:
            table_name (str): Name of the table to modify
            operations (list): List of operations like ["add column_name:type", "drop column_name"]
        """
        print(f"📝 Creating ALTER TABLE migration for '{table_name}' with operations: {', '.join(operations)}")
        self.generator.create_alter_migration(table_name, operations)
    
    def run_migrations(self):
        """Run all pending migrations."""
        self.runner.run_pending_migrations()
    
    def rollback_migrations(self):
        """Rollback the latest batch of migrations."""
        self.runner.rollback_last_batch()
    
    def run_specific_migration(self, migration_name, action):
        """Run a specific migration."""
        self.runner.run_migration(migration_name, action)
    
    def get_status(self):
        """Get the status of all migrations."""
        self.runner.get_migration_status()
    
    def get_all_migrations(self):
        """Get all migration files."""
        return self.generator.get_all_migrations()
    
    def get_applied_migrations(self):
        """Get all applied migrations."""
        return self.db_manager.get_applied_migrations()
    
    def get_pending_migrations(self):
        """Get all pending migrations."""
        applied = self.get_applied_migrations()
        all_migrations = self.get_all_migrations()
        return [m for m in all_migrations if m not in applied]
    
    def sync_orm_models(self):
        """Sync all ORM models with their corresponding migrations."""
        if not self.orm_generator:
            print("❌ ORM model generation is disabled. Enable GENERATE_ORM_MODELS in config.")
            return
        
        try:
            updated_models = self.orm_generator.sync_all_models(self.config.MIGRATION_FOLDER)
            if updated_models:
                print(f"✅ Synced {len(updated_models)} ORM models:")
                for model_path in updated_models:
                    print(f"  📝 {model_path}")
            else:
                print("✅ No ORM models to sync.")
        except Exception as e:
            print(f"❌ Error syncing ORM models: {e}")
    
    def generate_migrations_from_models(self, models_path: str, model_names: List[str] = None):
        """Generate migrations from existing ORM models."""
        try:
            generated_migrations = self.model_to_migration_generator.generate_migration_from_models(models_path, model_names)
            if generated_migrations:
                print(f"✅ Generated {len(generated_migrations)} migrations from models:")
                for migration_path in generated_migrations:
                    print(f"  📝 {migration_path}")
            else:
                print("❌ No migrations were generated.")
        except Exception as e:
            print(f"❌ Error generating migrations from models: {e}")
