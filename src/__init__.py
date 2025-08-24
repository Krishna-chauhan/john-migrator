"""
DB Migrator - A lightweight database migration tool for Python projects
"""

__version__ = "1.1.0"
__author__ = "John Doe"
__email__ = "krishnachauhan20993@gmail.com"

# Import legacy functions for backward compatibility
from .migrate import create_migration, create_alter_migration, run_pending_migrations, rollback_last_batch

# Import new class-based structure
from .migration_manager import MigrationManager
from .database_manager import DatabaseManager
from .migration_generator import MigrationGenerator
from .migration_runner import MigrationRunner

__all__ = [
    # Legacy functions
    "create_migration", 
    "create_alter_migration",
    "run_pending_migrations", 
    "rollback_last_batch",
    # New classes
    "MigrationManager",
    "DatabaseManager", 
    "MigrationGenerator",
    "MigrationRunner"
]
