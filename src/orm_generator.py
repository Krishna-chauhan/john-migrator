"""
ORM Model Generator for DB Migrator
Handles SQLAlchemy model generation and synchronization
"""

import os
import re
import ast
from typing import List, Dict, Optional


class ORMGenerator:
    """Handles ORM model generation and synchronization"""
    
    # SQL to SQLAlchemy type mapping
    TYPE_MAPPING = {
        'varchar': 'String',
        'char': 'String',
        'text': 'Text',
        'integer': 'Integer',
        'int': 'Integer',
        'bigint': 'BigInteger',
        'smallint': 'SmallInteger',
        'decimal': 'Float',
        'numeric': 'Float',
        'real': 'Float',
        'double': 'Float',
        'boolean': 'Boolean',
        'bool': 'Boolean',
        'timestamp': 'DateTime',
        'datetime': 'DateTime',
        'date': 'Date',
        'time': 'Time',
        'json': 'JSON',
        'uuid': 'String',
        'serial': 'Integer',
        'bigserial': 'BigInteger',
    }
    
    def __init__(self, config):
        self.config = config
        self.models_folder = config.MODELS_FOLDER
        self.base_class = config.ORM_BASE_CLASS
        self.imports = config.ORM_IMPORTS
        
        # Ensure models folder exists
        if not os.path.exists(self.models_folder):
            os.makedirs(self.models_folder)
    
    def generate_model(self, table_name: str, columns: List[str] = None) -> str:
        """Generate a SQLAlchemy model for the given table and columns.
        
        Args:
            table_name (str): Name of the table
            columns (list): List of column definitions
            
        Returns:
            str: Generated model code
        """
        class_name = "".join(word.capitalize() for word in table_name.split("_"))
        
        # Parse columns
        model_columns = self._parse_columns(columns) if columns else []
        
        # Generate model code
        model_code = f"""\
{self.imports}


class {class_name}({self.base_class}):
    __tablename__ = '{table_name}'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
"""
        
        # Add custom columns
        for column in model_columns:
            model_code += f"    {column}\n"
        
        # Add timestamp columns
        model_code += """\
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<{class_name}(id={{self.id}})>'
"""
        
        return model_code
    
    def _parse_columns(self, columns: List[str]) -> List[str]:
        """Parse column definitions and convert to SQLAlchemy format.
        
        Args:
            columns (list): List of column definitions like ["name:varchar(255)", "age:integer"]
            
        Returns:
            list: List of SQLAlchemy column definitions
        """
        model_columns = []
        
        for column_def in columns:
            if ':' not in column_def:
                continue
                
            col_name, col_type = column_def.split(':', 1)
            col_name = col_name.strip()
            
            # Parse SQL type and convert to SQLAlchemy
            sqlalchemy_type, constraints = self._convert_sql_type(col_type.strip())
            
            # Build column definition
            column_def = f"{col_name} = Column({sqlalchemy_type}"
            
            # Add constraints
            for constraint in constraints:
                column_def += f", {constraint}"
            
            column_def += ")"
            model_columns.append(column_def)
        
        return model_columns
    
    def _convert_sql_type(self, sql_type: str) -> tuple:
        """Convert SQL type to SQLAlchemy type with constraints.
        
        Args:
            sql_type (str): SQL type like "varchar(255)" or "integer"
            
        Returns:
            tuple: (sqlalchemy_type, [constraints])
        """
        # Extract base type and size
        base_type = sql_type.lower()
        size = None
        
        # Handle types with size like varchar(255)
        if '(' in sql_type:
            match = re.match(r'(\w+)\((\d+)(?:,\s*(\d+))?\)', sql_type.lower())
            if match:
                base_type = match.group(1)
                size = int(match.group(2))
                precision = match.group(3)
        
        # Get SQLAlchemy type
        sqlalchemy_type = self.TYPE_MAPPING.get(base_type, 'String')
        
        # Add size for String types
        if sqlalchemy_type == 'String' and size:
            sqlalchemy_type = f"String({size})"
        elif sqlalchemy_type == 'Float' and size and precision:
            sqlalchemy_type = f"Float({size}, {precision})"
        
        # Add constraints
        constraints = []
        if base_type in ['varchar', 'char', 'text']:
            constraints.append('nullable=True')
        
        return sqlalchemy_type, constraints
    
    def save_model(self, table_name: str, model_code: str) -> str:
        """Save the generated model to a file.
        
        Args:
            table_name (str): Name of the table
            model_code (str): Generated model code
            
        Returns:
            str: Path to the saved model file
        """
        class_name = "".join(word.capitalize() for word in table_name.split("_"))
        filename = f"{table_name}.py"
        filepath = os.path.join(self.models_folder, filename)
        
        with open(filepath, 'w') as f:
            f.write(model_code)
        
        # Set permissions
        os.chmod(filepath, 0o644)
        
        return filepath
    
    def update_model_from_migration(self, migration_file: str) -> Optional[str]:
        """Update or create model based on migration file.
        
        Args:
            migration_file (str): Path to migration file
            
        Returns:
            str: Path to updated model file, or None if no changes
        """
        # Parse migration file to extract table info
        table_info = self._parse_migration_file(migration_file)
        if not table_info:
            return None
        
        table_name = table_info['table_name']
        columns = table_info.get('columns', [])
        
        # Generate new model
        model_code = self.generate_model(table_name, columns)
        
        # Save model
        filepath = self.save_model(table_name, model_code)
        
        return filepath
    
    def _parse_migration_file(self, migration_file: str) -> Optional[Dict]:
        """Parse migration file to extract table information.
        
        Args:
            migration_file (str): Path to migration file
            
        Returns:
            dict: Table information or None
        """
        try:
            with open(migration_file, 'r') as f:
                content = f.read()
            
            # Extract table name from class
            table_match = re.search(r'self\.table_name\s*=\s*["\']([^"\']+)["\']', content)
            if not table_match:
                return None
            
            table_name = table_match.group(1)
            
            # Extract columns from CREATE TABLE statement
            create_match = re.search(r'CREATE TABLE\s+\w+\s*\(([^)]+)\)', content, re.DOTALL)
            columns = []
            
            if create_match:
                columns_sql = create_match.group(1)
                # Parse individual columns
                column_lines = [line.strip() for line in columns_sql.split('\n') if line.strip()]
                
                for line in column_lines:
                    # Skip id, created_at, updated_at columns (handled automatically)
                    if any(skip in line.lower() for skip in ['id serial', 'created_at', 'updated_at']):
                        continue
                    
                    # Extract column name and type
                    col_match = re.match(r'(\w+)\s+([^,]+)', line)
                    if col_match:
                        col_name = col_match.group(1)
                        col_type = col_match.group(2).strip()
                        columns.append(f"{col_name}:{col_type}")
            
            return {
                'table_name': table_name,
                'columns': columns
            }
            
        except Exception as e:
            print(f"⚠️  Warning: Could not parse migration file {migration_file}: {e}")
            return None
    
    def sync_all_models(self, migration_folder: str) -> List[str]:
        """Sync all models with their corresponding migrations.
        
        Args:
            migration_folder (str): Path to migration folder
            
        Returns:
            list: List of updated model files
        """
        updated_models = []
        
        if not os.path.exists(migration_folder):
            return updated_models
        
        for filename in os.listdir(migration_folder):
            if filename.startswith('m_') and filename.endswith('.py'):
                migration_file = os.path.join(migration_folder, filename)
                model_file = self.update_model_from_migration(migration_file)
                if model_file:
                    updated_models.append(model_file)
        
        return updated_models
