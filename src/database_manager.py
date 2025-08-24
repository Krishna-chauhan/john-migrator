"""
Database Manager for DB Migrator
Handles database connections and operations
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

# Handle imports for both direct execution and package import
try:
    from .config import Config
except ImportError:
    # When running as script directly
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import Config


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.config = Config()
        self.engine = create_engine(self.config.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.migration_table = self.config.MIGRATION_TABLE
    
    def create_migration_table(self):
        """Creates the migrations table if it does not exist."""
        with self.SessionLocal() as session:
            session.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.migration_table} (
                    id SERIAL PRIMARY KEY,
                    migration VARCHAR(255) UNIQUE NOT NULL,
                    batch INT NOT NULL,
                    applied_at TIMESTAMP DEFAULT NOW()
                );
            """))
            session.commit()
        print("✅ Migration table ensured.")
    
    def get_applied_migrations(self):
        """Fetch applied migrations from the database."""
        try:
            with self.SessionLocal() as session:
                result = session.execute(text(f"SELECT migration FROM {self.migration_table}"))
                return {row[0] for row in result}
        except ProgrammingError:
            self.create_migration_table()
            return self.get_applied_migrations()
    
    def record_migration(self, migration_name, batch):
        """Record a migration as applied."""
        with self.SessionLocal() as session:
            session.execute(
                text(f"INSERT INTO {self.migration_table} (migration, batch) VALUES (:migration_name, :batch)"),
                {"migration_name": migration_name, "batch": batch}
            )
            session.commit()
    
    def remove_migration(self, migration_name):
        """Remove a migration record (for rollback)."""
        with self.SessionLocal() as session:
            session.execute(
                text(f"DELETE FROM {self.migration_table} WHERE migration = :migration_name"),
                {"migration_name": migration_name}
            )
            session.commit()
    
    def get_latest_batch(self):
        """Get the latest batch number."""
        with self.SessionLocal() as session:
            result = session.execute(text(f"SELECT MAX(batch) FROM {self.migration_table}"))
            return result.scalar()
    
    def get_migrations_by_batch(self, batch):
        """Get all migrations in a specific batch."""
        with self.SessionLocal() as session:
            result = session.execute(
                text(f"SELECT migration FROM {self.migration_table} WHERE batch = :batch"),
                {"batch": batch}
            )
            return [row[0] for row in result.fetchall()]
    
    def execute_sql(self, sql):
        """Execute SQL statement."""
        with self.SessionLocal() as session:
            session.execute(text(sql))
            session.commit()
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
