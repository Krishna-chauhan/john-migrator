"""
Model to Migration Generator for DB Migrator
Generates migrations from existing SQLAlchemy ORM models
"""

import os
import sys
import importlib
import inspect
import re
from typing import List, Dict, Optional, Any
from datetime import datetime


class ModelToMigrationGenerator:
    """Generates migrations from existing SQLAlchemy ORM models"""
    
    # SQLAlchemy to SQL type mapping (reverse of ORM generator)
    TYPE_MAPPING = {
        'String': 'varchar',
        'Text': 'text',
        'Integer': 'integer',
        'BigInteger': 'bigint',
        'SmallInteger': 'smallint',
        'Float': 'decimal',
        'Numeric': 'decimal',
        'Boolean': 'boolean',
        'DateTime': 'timestamp',
        'Date': 'date',
        'Time': 'time',
        'JSON': 'json',
        'UUID': 'uuid',
    }
    
    def __init__(self, config):
        self.config = config
        self.migration_folder = config.MIGRATION_FOLDER
        
        # Ensure migration folder exists
        if not os.path.exists(self.migration_folder):
            os.makedirs(self.migration_folder)
    
    def generate_migration_from_models(self, models_path: str, model_names: List[str] = None) -> List[str]:
        """Generate migrations from existing ORM models.
        
        Args:
            models_path (str): Path to the models directory or file
            model_names (list): List of specific model names to process (optional)
            
        Returns:
            list: List of generated migration file paths
        """
        generated_migrations = []
        
        try:
            # Load models
            models = self._load_models(models_path, model_names)
            
            if not models:
                print("❌ No models found to generate migrations from.")
                return generated_migrations
            
            print(f"📝 Found {len(models)} models to process...")
            
            # Generate migration for each model
            for model_name, model_class in models.items():
                migration_file = self._generate_migration_for_model(model_name, model_class)
                if migration_file:
                    generated_migrations.append(migration_file)
            
            return generated_migrations
            
        except Exception as e:
            print(f"❌ Error generating migrations from models: {e}")
            return generated_migrations
    
    def _load_models(self, models_path: str, model_names: List[str] = None) -> Dict[str, Any]:
        """Load SQLAlchemy models from the given path.
        
        Args:
            models_path (str): Path to models directory or file
            model_names (list): Specific model names to load
            
        Returns:
            dict: Dictionary of model_name -> model_class
        """
        models = {}
        
        if os.path.isfile(models_path):
            # Single file
            models.update(self._load_models_from_file(models_path, model_names))
        elif os.path.isdir(models_path):
            # Directory
            for filename in os.listdir(models_path):
                if filename.endswith('.py') and not filename.startswith('__'):
                    file_path = os.path.join(models_path, filename)
                    models.update(self._load_models_from_file(file_path, model_names))
        
        return models
    
    def _load_models_from_file(self, file_path: str, model_names: List[str] = None) -> Dict[str, Any]:
        """Load models from a single Python file.
        
        Args:
            file_path (str): Path to the Python file
            model_names (list): Specific model names to load
            
        Returns:
            dict: Dictionary of model_name -> model_class
        """
        models = {}
        
        try:
            # Add the directory to Python path
            file_dir = os.path.dirname(os.path.abspath(file_path))
            if file_dir not in sys.path:
                sys.path.insert(0, file_dir)
            
            # Import the module
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            module = importlib.import_module(module_name)
            
            # Find SQLAlchemy model classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if self._is_sqlalchemy_model(obj):
                    # Check if we want this specific model
                    if model_names is None or name in model_names:
                        models[name] = obj
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load models from {file_path}: {e}")
        
        return models
    
    def _is_sqlalchemy_model(self, obj) -> bool:
        """Check if an object is a SQLAlchemy model.
        
        Args:
            obj: Object to check
            
        Returns:
            bool: True if it's a SQLAlchemy model
        """
        try:
            # Check for SQLAlchemy model attributes
            has_tablename = hasattr(obj, '__tablename__')
            has_columns = hasattr(obj, '__table__')
            
            # Check if it inherits from a SQLAlchemy base
            bases = obj.__bases__
            sqlalchemy_base = any('sqlalchemy' in str(base).lower() for base in bases)
            
            return has_tablename and has_columns and sqlalchemy_base
            
        except Exception:
            return False
    
    def _generate_migration_for_model(self, model_name: str, model_class) -> Optional[str]:
        """Generate a migration file for a single model.
        
        Args:
            model_name (str): Name of the model class
            model_class: The SQLAlchemy model class
            
        Returns:
            str: Path to generated migration file, or None if failed
        """
        try:
            # Get table information
            table_name = getattr(model_class, '__tablename__', model_name.lower())
            columns = self._extract_columns_from_model(model_class)
            
            # Generate migration content
            migration_content = self._create_migration_content(model_name, table_name, columns)
            
            # Save migration file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"m_{timestamp}_create_{table_name}_table.py"
            filepath = os.path.join(self.migration_folder, filename)
            
            with open(filepath, 'w') as f:
                f.write(migration_content)
            
            # Set permissions
            os.chmod(filepath, 0o644)
            
            print(f"✅ Generated migration for {model_name}: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error generating migration for {model_name}: {e}")
            return None
    
    def _extract_columns_from_model(self, model_class) -> List[Dict]:
        """Extract column information from a SQLAlchemy model.
        
        Args:
            model_class: The SQLAlchemy model class
            
        Returns:
            list: List of column dictionaries
        """
        columns = []
        
        try:
            # Get all attributes that are Column instances
            for attr_name, attr_value in inspect.getmembers(model_class):
                if hasattr(attr_value, 'type') and hasattr(attr_value, 'name'):
                    # Skip primary key and timestamp columns (handled automatically)
                    if attr_name in ['id', 'created_at', 'updated_at']:
                        continue
                    
                    column_info = self._extract_column_info(attr_name, attr_value)
                    if column_info:
                        columns.append(column_info)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not extract columns from model: {e}")
        
        return columns
    
    def _extract_column_info(self, attr_name: str, column) -> Optional[Dict]:
        """Extract information from a SQLAlchemy Column.
        
        Args:
            attr_name (str): Name of the attribute
            column: SQLAlchemy Column instance
            
        Returns:
            dict: Column information or None
        """
        try:
            column_type = type(column.type).__name__
            sql_type = self.TYPE_MAPPING.get(column_type, 'varchar')
            
            # Handle String with length
            if column_type == 'String' and hasattr(column.type, 'length'):
                sql_type = f"varchar({column.type.length})"
            
            # Handle Float with precision
            elif column_type == 'Float' and hasattr(column.type, 'precision'):
                precision = column.type.precision
                scale = getattr(column.type, 'scale', 0)
                sql_type = f"decimal({precision},{scale})"
            
            # Build constraints
            constraints = []
            if not getattr(column, 'nullable', True):
                constraints.append('NOT NULL')
            
            if getattr(column, 'unique', False):
                constraints.append('UNIQUE')
            
            if hasattr(column, 'default') and column.default is not None:
                default_value = self._format_default_value(column.default)
                if default_value:
                    constraints.append(f"DEFAULT {default_value}")
            
            return {
                'name': attr_name,
                'type': sql_type,
                'constraints': constraints
            }
            
        except Exception as e:
            print(f"⚠️  Warning: Could not extract info for column {attr_name}: {e}")
            return None
    
    def _format_default_value(self, default) -> Optional[str]:
        """Format a default value for SQL.
        
        Args:
            default: Default value from SQLAlchemy
            
        Returns:
            str: Formatted default value or None
        """
        try:
            if hasattr(default, 'arg'):
                # SQLAlchemy function default
                if hasattr(default.arg, '__name__'):
                    if default.arg.__name__ == 'now':
                        return 'NOW()'
                    elif default.arg.__name__ == 'utcnow':
                        return 'NOW()'
                return str(default.arg)
            else:
                # Simple value default
                if isinstance(default, str):
                    return f"'{default}'"
                elif isinstance(default, bool):
                    return 'TRUE' if default else 'FALSE'
                else:
                    return str(default)
        except Exception:
            return None
    
    def _create_migration_content(self, model_name: str, table_name: str, columns: List[Dict]) -> str:
        """Create the migration file content.
        
        Args:
            model_name (str): Name of the model class
            table_name (str): Name of the table
            columns (list): List of column information
            
        Returns:
            str: Migration file content
        """
        # Generate column SQL
        column_sql = []
        for column in columns:
            col_def = f"            {column['name']} {column['type'].upper()}"
            if column['constraints']:
                col_def += f" {' '.join(column['constraints'])}"
            col_def += ","
            column_sql.append(col_def)
        
        columns_text = "\n".join(column_sql) if column_sql else "            name VARCHAR(255),"
        
        # Create migration template
        migration_template = f"""from john_migrator.migrations.base_migration import BaseMigration

class {model_name}(BaseMigration):
    def __init__(self):
        self.table_name = "{table_name}"

    def up(self):
        return \"\"\"
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
{columns_text}
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        \"\"\"

    def down(self):
        return f'DROP TABLE IF EXISTS "{table_name}";'
"""
        
        return migration_template
    
    def generate_migration_from_model_file(self, model_file: str, model_name: str = None) -> Optional[str]:
        """Generate migration from a single model file.
        
        Args:
            model_file (str): Path to the model file
            model_name (str): Specific model name to generate migration for
            
        Returns:
            str: Path to generated migration file, or None if failed
        """
        model_names = [model_name] if model_name else None
        migrations = self.generate_migration_from_models(model_file, model_names)
        return migrations[0] if migrations else None
