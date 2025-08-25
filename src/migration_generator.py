"""
Migration Generator for DB Migrator
Handles migration file creation and template generation
"""

import os
import datetime
import sys

# Handle imports for both direct execution and package import
try:
    from .config import Config
    from .orm_generator import ORMGenerator
except ImportError:
    # When running as script directly
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import Config
    from orm_generator import ORMGenerator


class MigrationGenerator:
    """Handles migration file generation and template management"""
    
    MIGRATION_TEMPLATE = """\
from john_migrator.migrations.base_migration import BaseMigration

class {class_name}(BaseMigration):
    def __init__(self):
        self.table_name = "{table_name}"

    def up(self):
        return \"\"\"
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
{columns}
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        \"\"\"

    def down(self):
        return f'DROP TABLE IF EXISTS "{table_name}";'
"""

    ALTER_TABLE_TEMPLATE = """\
from john_migrator.migrations.base_migration import BaseMigration

class {class_name}(BaseMigration):
    def __init__(self):
        self.table_name = "{table_name}"

    def up(self):
        return \"\"\"
{alter_statements}
        \"\"\"

    def down(self):
        return \"\"\"
{rollback_statements}
        \"\"\"
"""
    
    def __init__(self):
        self.config = Config()
        self.migration_folder = self.config.MIGRATION_FOLDER
        self.orm_generator = ORMGenerator(self.config) if self.config.GENERATE_ORM_MODELS else None
    
    def create_migration(self, migration_name, columns=None):
        """Generates a new migration file with optional column definitions.
        
        Args:
            migration_name (str): Name of the migration/table
            columns (list): List of column definitions in format ["name:type", "age:INTEGER"]
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"m_{timestamp}_{migration_name}.py"
        filepath = os.path.join(self.migration_folder, filename)

        class_name = "".join(word.capitalize() for word in migration_name.split("_"))
        columns_sql = self._process_columns(columns)

        if not os.path.exists(self.migration_folder):
            os.makedirs(self.migration_folder)

        with open(filepath, "w") as f:
            f.write(self.MIGRATION_TEMPLATE.format(
                class_name=class_name, 
                table_name=migration_name,
                columns=columns_sql
            ))

        # Explicitly set writable permissions
        os.chmod(filepath, 0o644)  # rw-r--r--
        print(f"✅ Migration '{filename}' created successfully at {filepath}.")
        
        if columns:
            print(f"📋 Columns defined: {', '.join(columns)}")
        
        # Generate ORM model if enabled
        if self.orm_generator:
            try:
                model_file = self.orm_generator.generate_model(migration_name, columns)
                model_path = self.orm_generator.save_model(migration_name, model_file)
                print(f"📝 ORM model generated at {model_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not generate ORM model: {e}")
    
    def create_alter_migration(self, table_name, operations):
        """Generates an ALTER TABLE migration file.
        
        Args:
            table_name (str): Name of the table to modify
            operations (list): List of operations in format ["add column_name:type", "drop column_name", "modify column_name:new_type"]
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        migration_name = f"alter_{table_name}"
        filename = f"m_{timestamp}_{migration_name}.py"
        filepath = os.path.join(self.migration_folder, filename)

        class_name = "".join(word.capitalize() for word in migration_name.split("_"))
        
        alter_statements, rollback_statements = self._process_alter_operations(table_name, operations)

        if not os.path.exists(self.migration_folder):
            os.makedirs(self.migration_folder)

        with open(filepath, "w") as f:
            f.write(self.ALTER_TABLE_TEMPLATE.format(
                class_name=class_name, 
                table_name=table_name,
                alter_statements=alter_statements,
                rollback_statements=rollback_statements
            ))

        # Explicitly set writable permissions
        os.chmod(filepath, 0o644)  # rw-r--r--
        print(f"✅ ALTER TABLE migration '{filename}' created successfully at {filepath}.")
        print(f"📋 Operations: {', '.join(operations)}")
    
    def _process_columns(self, columns):
        """Process column definitions into SQL format."""
        if not columns:
            return "            name VARCHAR(255),"
        
        column_lines = []
        for column_def in columns:
            if ":" in column_def:
                col_name, col_type = column_def.split(":", 1)
                column_lines.append(f"            {col_name.strip()} {col_type.strip().upper()},")
            else:
                # If no type specified, default to VARCHAR(255)
                column_lines.append(f"            {column_def.strip()} VARCHAR(255),")
        
        return "\n".join(column_lines)
    
    def _process_alter_operations(self, table_name, operations):
        """Process ALTER TABLE operations into SQL statements."""
        alter_lines = []
        rollback_lines = []
        
        for operation in operations:
            operation = operation.strip().lower()
            
            if operation.startswith("add "):
                # Add column: "add column_name:type"
                parts = operation[4:].split(":", 1)
                if len(parts) == 2:
                    col_name, col_type = parts
                    alter_lines.append(f"        ALTER TABLE {table_name} ADD COLUMN {col_name.strip()} {col_type.strip().upper()};")
                    rollback_lines.append(f"        ALTER TABLE {table_name} DROP COLUMN {col_name.strip()};")
                else:
                    print(f"⚠️  Warning: Invalid add operation format: {operation}")
            
            elif operation.startswith("drop "):
                # Drop column: "drop column_name"
                col_name = operation[5:].strip()
                alter_lines.append(f"        ALTER TABLE {table_name} DROP COLUMN {col_name};")
                # Note: Rollback for drop column is complex, would need to know original type
                rollback_lines.append(f"        -- ALTER TABLE {table_name} ADD COLUMN {col_name} <original_type>; -- Manual rollback required")
            
            elif operation.startswith("modify "):
                # Modify column: "modify column_name:new_type"
                parts = operation[7:].split(":", 1)
                if len(parts) == 2:
                    col_name, new_type = parts
                    alter_lines.append(f"        ALTER TABLE {table_name} ALTER COLUMN {col_name.strip()} TYPE {new_type.strip().upper()};")
                    rollback_lines.append(f"        -- ALTER TABLE {table_name} ALTER COLUMN {col_name.strip()} TYPE <original_type>; -- Manual rollback required")
                else:
                    print(f"⚠️  Warning: Invalid modify operation format: {operation}")
            
            elif operation.startswith("rename "):
                # Rename column: "rename old_name:new_name"
                parts = operation[7:].split(":", 1)
                if len(parts) == 2:
                    old_name, new_name = parts
                    alter_lines.append(f"        ALTER TABLE {table_name} RENAME COLUMN {old_name.strip()} TO {new_name.strip()};")
                    rollback_lines.append(f"        ALTER TABLE {table_name} RENAME COLUMN {new_name.strip()} TO {old_name.strip()};")
                else:
                    print(f"⚠️  Warning: Invalid rename operation format: {operation}")
            
            else:
                print(f"⚠️  Warning: Unknown operation: {operation}")
        
        return "\n".join(alter_lines), "\n".join(rollback_lines)
    
    def get_all_migrations(self):
        """Fetch all migration filenames from the migrations folder."""
        if not os.path.exists(self.migration_folder):
            return []
        
        return sorted(
            [f[:-3] for f in os.listdir(self.migration_folder) 
             if f.endswith(".py") and f.startswith("m_")]
        )
    
    def migration_exists(self, migration_name):
        """Check if a migration file exists."""
        return os.path.exists(os.path.join(self.migration_folder, f"{migration_name}.py"))
