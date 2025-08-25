"""
Migration Runner for DB Migrator
Handles migration execution and rollback operations
"""

import os
import sys
import importlib
import inspect
from sqlalchemy.exc import SQLAlchemyError

# Handle imports for both direct execution and package import
try:
    from .config import Config
    from .database_manager import DatabaseManager
    from .orm_generator import ORMGenerator
except ImportError:
    # When running as script directly
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import Config
    from database_manager import DatabaseManager
    from orm_generator import ORMGenerator


class MigrationRunner:
    """Handles migration execution and rollback operations"""
    
    def __init__(self):
        self.config = Config()
        self.migration_folder = self.config.MIGRATION_FOLDER
        self.db_manager = DatabaseManager()
        self.orm_generator = ORMGenerator(self.config) if self.config.GENERATE_ORM_MODELS else None
    
    def run_migration(self, migration_name, action):
        """Run a migration dynamically from the migrations folder.
        
        Args:
            migration_name (str): Name of the migration to run
            action (str): 'up' to apply, 'down' to rollback
        """
        try:
            print(f"🔄 Running migration: {migration_name} ({action})")

            # Add migration folder to Python path for dynamic imports
            if self.migration_folder not in sys.path:
                sys.path.insert(0, self.migration_folder)

            # Import the migration module
            module = importlib.import_module(migration_name)
            migration_class = self._find_migration_class(module)
            migration = migration_class()

            if action == "up":
                self._apply_migration(migration_name, migration)
            elif action == "down":
                self._rollback_migration(migration_name, migration)
            else:
                print("❌ Invalid action! Use 'up' or 'down'.")

        except ImportError:
            print(f"❌ Migration '{migration_name}' not found.")
        except SQLAlchemyError as e:
            print(f"❌ Database error in '{migration_name}': {e}")
        except Exception as e:
            print(f"❌ Unexpected error in '{migration_name}': {e}")
    
    def _find_migration_class(self, module):
        """Dynamically find and return the first class in the module."""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                return obj  # Return the first class found
        raise ImportError(f"❌ No valid migration class found in '{module.__name__}'")
    
    def _apply_migration(self, migration_name, migration):
        """Apply a migration."""
        self.db_manager.execute_sql(migration.up())
        
        # Record the migration
        latest_batch = self.db_manager.get_latest_batch()
        new_batch = (latest_batch or 0) + 1
        self.db_manager.record_migration(migration_name, new_batch)
        
        print(f"✅ Migration {migration_name} applied.")
        
        # Sync ORM model if enabled
        if self.orm_generator:
            try:
                migration_file = os.path.join(self.migration_folder, f"{migration_name}.py")
                if os.path.exists(migration_file):
                    model_path = self.orm_generator.update_model_from_migration(migration_file)
                    if model_path:
                        print(f"📝 ORM model updated: {model_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not sync ORM model: {e}")
    
    def _rollback_migration(self, migration_name, migration):
        """Rollback a migration."""
        self.db_manager.execute_sql(migration.down())
        self.db_manager.remove_migration(migration_name)
        print(f"✅ Migration {migration_name} rolled back.")
    
    def run_pending_migrations(self):
        """Run all migrations that are not in the database."""
        applied = self.db_manager.get_applied_migrations()
        all_migrations = self._get_all_migrations()
        pending_migrations = [m for m in all_migrations if m not in applied]

        if not pending_migrations:
            print("✅ No new migrations to apply.")
            return

        print(f"🚀 Applying {len(pending_migrations)} pending migrations...")
        for migration in pending_migrations:
            self.run_migration(migration, "up")
    
    def rollback_last_batch(self):
        """Rollback the last applied migration batch."""
        last_batch = self.db_manager.get_latest_batch()

        if last_batch is None:
            print("❌ No migrations to rollback.")
            return

        migrations_to_rollback = self.db_manager.get_migrations_by_batch(last_batch)

        print(f"🔄 Rolling back batch {last_batch} ({len(migrations_to_rollback)} migrations)...")
        for migration in migrations_to_rollback:
            self.run_migration(migration, "down")
    
    def _get_all_migrations(self):
        """Get all migration filenames from the migrations folder."""
        if not os.path.exists(self.migration_folder):
            return []
        
        return sorted(
            [f[:-3] for f in os.listdir(self.migration_folder) 
             if f.endswith(".py") and f.startswith("m_")]
        )
    
    def get_migration_status(self):
        """Get the status of all migrations."""
        applied = self.db_manager.get_applied_migrations()
        all_migrations = self._get_all_migrations()
        
        print("📊 Migration Status:")
        print("=" * 50)
        
        for migration in all_migrations:
            status = "✅ Applied" if migration in applied else "⏳ Pending"
            print(f"{migration}: {status}")
        
        pending_count = len([m for m in all_migrations if m not in applied])
        applied_count = len(applied)
        
        print("=" * 50)
        print(f"Total: {len(all_migrations)} migrations")
        print(f"Applied: {applied_count}")
        print(f"Pending: {pending_count}")
