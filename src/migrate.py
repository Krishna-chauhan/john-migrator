"""
Legacy migration interface for backward compatibility
This file maintains the old interface while using the new class-based structure
"""

import sys
from .migration_manager import MigrationManager


def create_migration(migration_name, columns=None):
    """Legacy function for creating migrations."""
    manager = MigrationManager()
    manager.create_migration(migration_name, columns)


def create_alter_migration(table_name, operations):
    """Legacy function for creating ALTER TABLE migrations."""
    manager = MigrationManager()
    manager.create_alter_migration(table_name, operations)


def run_pending_migrations():
    """Legacy function for running pending migrations."""
    manager = MigrationManager()
    manager.run_migrations()


def rollback_last_batch():
    """Legacy function for rolling back migrations."""
    manager = MigrationManager()
    manager.rollback_migrations()


def main():
    """Legacy main function for backward compatibility."""
    if len(sys.argv) < 2:
        print("Usage: john-migrator <up/down/create/alter/init>")
        print("\nCommands:")
        print("  init    - Create a default configuration file")
        print("  create  - Create a new migration file")
        print("  alter   - Create an ALTER TABLE migration")
        print("  up      - Apply pending migrations")
        print("  down    - Rollback the latest migration")
        print("\nExamples:")
        print("  john-migrator init")
        print("  john-migrator create users")
        print("  john-migrator create users name:varchar(255) age:integer email:varchar(100)")
        print("  john-migrator alter users add age:integer add email:varchar(100)")
        print("  john-migrator up")
        print("  john-migrator down")
        sys.exit(1)

    action = sys.argv[1]
    manager = MigrationManager()

    try:
        if action == "up":
            manager.run_migrations()
        elif action == "down":
            manager.rollback_migrations()
        elif action == "create":
            if len(sys.argv) < 3:
                print("❌ Missing migration name for 'create' command.")
                print("Usage: john-migrator create <migration_name> [column1:type1 column2:type2 ...]")
                sys.exit(1)
            
            migration_name = sys.argv[2]
            columns = sys.argv[3:] if len(sys.argv) > 3 else None
            
            if columns:
                print(f"📝 Creating migration '{migration_name}' with columns: {', '.join(columns)}")
            else:
                print(f"📝 Creating migration '{migration_name}' with default columns")
            
            manager.create_migration(migration_name, columns)
        elif action == "alter":
            if len(sys.argv) < 4:
                print("❌ Missing arguments for 'alter' command.")
                print("Usage: john-migrator alter <table_name> <operation1> [operation2 ...]")
                print("\nOperations:")
                print("  add column_name:type     - Add a new column")
                print("  drop column_name         - Drop an existing column")
                print("  modify column_name:type  - Modify column type")
                print("  rename old_name:new_name - Rename a column")
                sys.exit(1)
            
            table_name = sys.argv[2]
            operations = sys.argv[3:]
            manager.create_alter_migration(table_name, operations)
        elif action == "init":
            manager.init_project()
        else:
            print("❌ Invalid command! Use 'init', 'up', 'down', 'create', or 'alter'.")
            print("Run 'john-migrator' without arguments for usage examples.")
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
