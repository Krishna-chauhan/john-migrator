"""
Command Line Interface for DB Migrator
Handles command line argument parsing and execution
"""

import sys
from .migration_manager import MigrationManager


def show_help():
    """Display help information."""
    print("Usage: john-migrator <command> [options]")
    print("\nCommands:")
    print("  init    - Create a default configuration file")
    print("  create  - Create a new migration file")
    print("  alter   - Create an ALTER TABLE migration")
    print("  up      - Apply pending migrations")
    print("  down    - Rollback the latest migration")
    print("  status  - Show migration status")
    print("  run     - Run a specific migration")
    print("  sync    - Sync ORM models with migrations")
    print("  from-model - Generate migrations from existing ORM models")
    print("\nExamples:")
    print("  john-migrator init")
    print("  john-migrator create users")
    print("  john-migrator create users name:varchar(255) age:integer email:varchar(100)")
    print("  john-migrator alter users add age:integer add email:varchar(100)")
    print("  john-migrator alter users drop old_column modify name:varchar(500)")
    print("  john-migrator up")
    print("  john-migrator down")
    print("  john-migrator status")
    print("  john-migrator run m_20250101120000_create_users up")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1]
    manager = MigrationManager()

    try:
        if command == "init":
            manager.init_project()
        
        elif command == "create":
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
        
        elif command == "alter":
            if len(sys.argv) < 4:
                print("❌ Missing arguments for 'alter' command.")
                print("Usage: john-migrator alter <table_name> <operation1> [operation2 ...]")
                print("\nOperations:")
                print("  add column_name:type     - Add a new column")
                print("  drop column_name         - Drop an existing column")
                print("  modify column_name:type  - Modify column type")
                print("  rename old_name:new_name - Rename a column")
                print("\nExamples:")
                print("  john-migrator alter users add age:integer add email:varchar(100)")
                print("  john-migrator alter users drop old_column modify name:varchar(500)")
                sys.exit(1)
            
            table_name = sys.argv[2]
            operations = sys.argv[3:]
            
            # Format operations properly for the migration generator
            formatted_operations = []
            i = 0
            while i < len(operations):
                if operations[i] in ['add', 'drop', 'modify', 'rename']:
                    if i + 1 < len(operations):
                        formatted_operations.append(f"{operations[i]} {operations[i+1]}")
                        i += 2
                    else:
                        print(f"⚠️  Warning: Incomplete operation: {operations[i]}")
                        i += 1
                else:
                    print(f"⚠️  Warning: Unknown operation: {operations[i]}")
                    i += 1
            
            manager.create_alter_migration(table_name, formatted_operations)
        
        elif command == "up":
            manager.run_migrations()
        
        elif command == "down":
            manager.rollback_migrations()
        
        elif command == "status":
            manager.get_status()
        
        elif command == "run":
            if len(sys.argv) < 4:
                print("❌ Missing arguments for 'run' command.")
                print("Usage: john-migrator run <migration_name> <up|down>")
                sys.exit(1)
            
            migration_name = sys.argv[2]
            action = sys.argv[3]
            
            if action not in ["up", "down"]:
                print("❌ Invalid action! Use 'up' or 'down'.")
                sys.exit(1)
        
        elif command == "sync":
            print("🔄 Syncing ORM models with migrations...")
            manager.sync_orm_models()
        
        elif command == "from-model":
            if len(sys.argv) < 3:
                print("❌ Missing models path for 'from-model' command.")
                print("Usage: john-migrator from-model <models_path> [model_name1 model_name2 ...]")
                print("\nExamples:")
                print("  john-migrator from-model ./models")
                print("  john-migrator from-model ./models/user.py")
                print("  john-migrator from-model ./models User Product")
                sys.exit(1)
            
            models_path = sys.argv[2]
            model_names = sys.argv[3:] if len(sys.argv) > 3 else None
            
            if model_names:
                print(f"📝 Generating migrations from {models_path} for models: {', '.join(model_names)}")
            else:
                print(f"📝 Generating migrations from all models in {models_path}")
            
            manager.generate_migrations_from_models(models_path, model_names)
        
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
