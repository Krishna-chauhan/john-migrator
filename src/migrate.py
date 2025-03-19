import os
import importlib
import sys
import inspect
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from config import Config


config = Config()
DATABASE_URL = config.DATABASE_URL
MIGRATION_FOLDER = config.MIGRATION_TABLE
MIGRATION_TABLE = config.MIGRATION_TABLE

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

MIGRATION_TEMPLATE = """\
from src.database.base_migration import BaseMigration

class {class_name}(BaseMigration):
    def __init__(self):
        self.table_name = "{table_name}"

    def up(self):
        return \"\"\"
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        \"\"\"

    def down(self):
        return f'DROP TABLE IF EXISTS "{table_name}";'
"""


def create_migration(migration_name):
    """Generates a new migration file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"m_{timestamp}_{migration_name}.py"
    filepath = os.path.join(MIGRATION_FOLDER, filename)

    class_name = "".join(word.capitalize() for word in migration_name.split("_"))

    if not os.path.exists(MIGRATION_FOLDER):
        os.makedirs(MIGRATION_FOLDER)

    with open(filepath, "w") as f:
        f.write(MIGRATION_TEMPLATE.format(class_name=class_name, table_name=migration_name))

    # Explicitly set writable permissions
    os.chmod(filepath, 0o644)  # rw-r--r--
    print(f"✅ Migration '{filename}' created successfully at {filepath}.")


def create_migration_table():
    """Creates the migrations table if it does not exist."""
    with SessionLocal() as session:
        session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {MIGRATION_TABLE} (
                id SERIAL PRIMARY KEY,
                migration VARCHAR(255) UNIQUE NOT NULL,
                batch INT NOT NULL,
                applied_at TIMESTAMP DEFAULT NOW()
            );
        """))
        session.commit()
    print("✅ Migration table ensured.")


def find_migration_class(module):
    """Dynamically find and return the first class in the module."""
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            return obj  # Return the first class found
    raise ImportError(f"❌ No valid migration class found in '{module.__name__}'")


def get_applied_migrations():
    """Fetch applied migrations from the database."""
    try:
        with SessionLocal() as session:
            result = session.execute(text(f"SELECT migration FROM {MIGRATION_TABLE}"))
            return {row[0] for row in result}
    except ProgrammingError:
        create_migration_table()
        return get_applied_migrations()


def get_all_migrations():
    """Fetch all migration filenames from the `migrations` folder."""
    return sorted(
        [f[:-3] for f in os.listdir(MIGRATION_FOLDER) if f.endswith(".py") and f.startswith("m_")]
    )


def run_migration(migration_name, action):
    """Run a migration dynamically from the migrations folder."""
    try:
        module_path = MIGRATION_FOLDER.replace("/", ".")
        print(f"🔄 Running migration: {migration_name} ({action})")

        module = importlib.import_module(f'{module_path}.{migration_name}')
        migration_class = find_migration_class(module)
        migration = migration_class()

        with SessionLocal() as session:
            if action == "up":
                session.execute(text(migration.up()))
                latest_batch = session.execute(text(f"SELECT MAX(batch) FROM {MIGRATION_TABLE}"))
                new_batch = (latest_batch.scalar() or 0) + 1
                session.execute(
                    text(f"INSERT INTO {MIGRATION_TABLE} (migration, batch) VALUES (:migration_name, :batch)"),
                    {"migration_name": migration_name, "batch": new_batch})
                session.commit()
                print(f"✅ Migration {migration_name} applied.")

            elif action == "down":
                session.execute(text(migration.down()))
                session.execute(text(f"DELETE FROM {MIGRATION_TABLE} WHERE migration = :migration_name"),
                                {"migration_name": migration_name})
                session.commit()
                print(f"✅ Migration {migration_name} rolled back.")

            else:
                print("❌ Invalid action! Use 'up' or 'down'.")

    except ImportError:
        print(f"❌ Migration '{migration_name}' not found.")
    except SQLAlchemyError as e:
        print(f"❌ Database error in '{migration_name}': {e}")
    except Exception as e:
        print(f"❌ Unexpected error in '{migration_name}': {e}")


def run_pending_migrations():
    """Run all migrations that are not in the database."""
    applied = get_applied_migrations()
    all_migrations = get_all_migrations()
    pending_migrations = [m for m in all_migrations if m not in applied]

    if not pending_migrations:
        print("✅ No new migrations to apply.")
        return

    print(f"🚀 Applying {len(pending_migrations)} pending migrations...")
    for migration in pending_migrations:
        run_migration(migration, "up")


def rollback_last_batch():
    """Rollback the last applied migration batch."""
    with SessionLocal() as session:
        last_batch = session.execute(text(f"SELECT MAX(batch) FROM {MIGRATION_TABLE}"))
        last_batch = last_batch.scalar()

        if last_batch is None:
            print("❌ No migrations to rollback.")
            return

        migrations_to_rollback = session.execute(
            text(f"SELECT migration FROM {MIGRATION_TABLE} WHERE batch = :batch"),
            {"batch": last_batch}
        ).fetchall()

        for migration in migrations_to_rollback:
            run_migration(migration[0], "down")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <up/down>")
        sys.exit(1)

    action = sys.argv[1]

    if action == "up":
        run_pending_migrations()
    elif action == "down":
        rollback_last_batch()
    elif action == "create":
        command = sys.argv[1]
        migration_name = sys.argv[2]
        create_migration(migration_name)
    else:
        print("❌ Invalid command! Use 'up' to apply new migrations , 'down' to rollback. and 'create' to create a new "
              "migration.")
