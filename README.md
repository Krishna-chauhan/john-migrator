# 🚀 **DB Migrator**

A lightweight database migration tool for managing and automating schema changes effortlessly.

---

## 📋 Requirements

- **Python**: 3.7 or higher
- **Database**: PostgreSQL (primary) or MySQL
- **Dependencies**: SQLAlchemy 2.0+, psycopg2-binary, python-dotenv

### 🐍 Python Version Compatibility

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.7 | ✅ Supported | Minimum required version |
| 3.8 | ✅ Supported | Full compatibility |
| 3.9 | ✅ Supported | Full compatibility |
| 3.10 | ✅ Supported | Full compatibility |
| 3.11 | ✅ Supported | Full compatibility |
| 3.12 | ✅ Supported | Full compatibility |
| 3.6 | ❌ Not Supported | Missing f-string support |

**Note**: Python 3.7+ is required due to the use of f-strings and modern importlib features.

---

## 📦 Features

- ✅ Seamless migration management — apply and rollback with ease
- ✅ Tracks applied migrations using a `schema_migrations` table
- ✅ Supports both **PostgreSQL** and **MySQL**
- ✅ Robust error handling and detailed logging
- ✅ Works in any Python project directory
- ✅ **NEW**: Define table columns when creating migrations
- ✅ **NEW**: Automatic SQLAlchemy ORM model generation
- ✅ **NEW**: ORM model synchronization with migrations
- ✅ **NEW**: Configurable ORM model folder and settings

---

## 🛠️ Installation

```bash
pip install john-migrator
```

## 🚀 Quick Start

### 1. Initialize Your Project

First, create a default configuration file:

```bash
john-migrator init
```

This creates a `john_migrator_config.py` file in your project root with default settings.

### 2. Configure Your Database

Edit the generated `john_migrator_config.py` file:

```python
# john_migrator_config.py
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "your_database"
MIGRATION_FOLDER = "migrations"  # Optional: defaults to ./migrations
```

Or use environment variables:

```bash
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=your_database
```

### 3. Create Your First Migration

#### Simple Migration (with default columns):
```bash
john-migrator create create_users_table
```

#### Migration with Custom Columns:
```bash
john-migrator create users username:varchar(255) age:integer email:varchar(100) is_active:boolean
```

This creates a migration file in your `migrations/` folder with the specified columns.

### 4. Edit the Migration (if needed)

Open the generated file and customize your SQL:

```python
from john_migrator.migrations.base_migration import BaseMigration

class Users(BaseMigration):
    def __init__(self):
        self.table_name = "users"

    def up(self):
        return """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255),
            age INTEGER,
            email VARCHAR(100),
            is_active BOOLEAN,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """

    def down(self):
        return 'DROP TABLE IF EXISTS "users";'
```

### 5. Run Migrations

```bash
# Apply all pending migrations
john-migrator up

# Rollback the latest migration
john-migrator down

# Create a new migration with columns
john-migrator create products name:varchar(255) price:decimal(10,2) category:varchar(100)

# Modify existing tables
john-migrator alter users add age:integer add email:varchar(100)
john-migrator alter products drop old_price rename product_name:name
```

---

## 🛠️ Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Create a default configuration file | `john-migrator init` |
| `create` | Create a new migration file | `john-migrator create users name:varchar(255) age:integer` |
| `alter` | Create an ALTER TABLE migration | `john-migrator alter users add age:integer add email:varchar(100)` |
| `up` | Apply pending migrations | `john-migrator up` |
| `down` | Rollback the latest migration | `john-migrator down` |
| `status` | Show migration status | `john-migrator status` |
| `run` | Run a specific migration | `john-migrator run m_20250101120000_create_users up` |
| `sync` | Sync ORM models with migrations | `john-migrator sync` |

### Command Details

#### `john-migrator init`
Creates a `john_migrator_config.py` file with default database and migration settings. This is the first command you should run in a new project.

#### `john-migrator create <name> [columns...]`
Creates a new migration file with the specified name and optional column definitions.

**Examples:**
```bash
# Simple migration
john-migrator create users

# Migration with columns
john-migrator create products name:varchar(255) price:decimal(10,2) category:varchar(100)
```

#### `john-migrator alter <table> <operations...>`
Creates an ALTER TABLE migration to modify existing tables.

**Operations:**
- `add column_name:type` - Add a new column
- `drop column_name` - Drop an existing column  
- `modify column_name:new_type` - Modify column type
- `rename old_name:new_name` - Rename a column

**Examples:**
```bash
# Add columns
john-migrator alter users add age:integer add email:varchar(100)

# Drop and modify columns
john-migrator alter users drop old_column modify name:varchar(500)

# Rename columns
john-migrator alter products rename product_name:name

# Complex operations
john-migrator alter products add price:decimal(10,2) drop old_price rename product_name:name
```

#### `john-migrator up`
Applies all pending migrations that haven't been run yet.

#### `john-migrator down`
Rolls back the most recent batch of migrations.

#### `john-migrator status`
Shows the status of all migrations (applied vs pending).

#### `john-migrator run <migration> <action>`
Runs a specific migration with the specified action (up or down).

**Examples:**
```bash
john-migrator run m_20250101120000_create_users up
john-migrator run m_20250101120000_create_users down
```

---

## 🗃️ ORM Model Generation

**NEW**: DB Migrator now automatically generates SQLAlchemy ORM models when you create migrations!

### Automatic ORM Model Generation

When you create a migration, DB Migrator automatically generates a corresponding SQLAlchemy model:

```bash
# Create a migration with columns
john-migrator create users username:varchar(255) age:integer email:varchar(100) is_active:boolean
```

This will create:
1. **Migration file**: `migrations/m_20250101120000_users.py`
2. **ORM Model**: `models/users.py`

### Generated ORM Model Example

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, BigInteger, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Custom columns
    username = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<Users(id={self.id})>'
```

### ORM Configuration

Configure ORM model generation in your `john_migrator_config.py`:

```python
# ORM Model Configuration (optional)
MODELS_FOLDER = "models"  # Default: ./models
GENERATE_ORM_MODELS = True  # Set to False to disable ORM model generation
ORM_BASE_CLASS = "Base"  # SQLAlchemy base class name
```

### ORM Commands

| Command | Description | Example |
|---------|-------------|---------|
| `sync` | Sync all ORM models with migrations | `john-migrator sync` |

#### `john-migrator sync`
Synchronizes all ORM models with their corresponding migration files. Useful when:
- You've manually edited migration files
- You want to regenerate all models
- You've added new migrations from other sources

```bash
john-migrator sync
```

### ORM Model Synchronization

DB Migrator automatically syncs ORM models when:
- ✅ Creating new migrations with `create` command
- ✅ Applying migrations with `up` command
- ✅ Running the `sync` command manually

### Supported SQL to SQLAlchemy Type Mapping

| SQL Type | SQLAlchemy Type | Notes |
|----------|----------------|-------|
| `varchar(n)` | `String(n)` | Variable length string |
| `text` | `Text` | Long text |
| `integer` | `Integer` | Integer number |
| `bigint` | `BigInteger` | Large integer |
| `decimal(p,s)` | `Float(p,s)` | Decimal number |
| `boolean` | `Boolean` | True/False |
| `timestamp` | `DateTime` | Date and time |
| `date` | `Date` | Date only |
| `json` | `JSON` | JSON data |

---

## 🏗️ Architecture

The DB Migrator is built with a clean, modular architecture:

### Core Classes

- **`MigrationManager`** - Main orchestrator that coordinates all migration operations
- **`DatabaseManager`** - Handles database connections and operations
- **`MigrationGenerator`** - Creates migration files and manages templates
- **`MigrationRunner`** - Executes migrations and handles rollbacks

### File Structure

```
src/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── cli.py                   # Command line interface
├── migrate.py               # Legacy interface (backward compatibility)
├── migration_manager.py     # Main migration orchestrator
├── database_manager.py      # Database operations
├── migration_generator.py   # Migration file generation
├── migration_runner.py      # Migration execution
├── orm_generator.py         # ORM model generation
└── migrations/
    ├── __init__.py
    ├── base_migration.py    # Abstract base class
    └── *.py                 # Generated migration files
```

### Usage in Code

You can also use the package programmatically:

```python
from john_migrator import MigrationManager

# Initialize the manager
manager = MigrationManager()

# Create a migration
manager.create_migration("users", ["name:varchar(255)", "age:integer"])

# Run migrations
manager.run_migrations()

# Check status
manager.get_status()
```

---

## 🔄 ALTER TABLE Operations

The `alter` command supports various table modification operations:

### Supported Operations

| Operation | Syntax | Description | Rollback |
|-----------|--------|-------------|----------|
| **Add Column** | `add column_name:type` | Adds a new column to the table | ✅ Automatic (drops column) |
| **Drop Column** | `drop column_name` | Removes a column from the table | ⚠️ Manual (requires original type) |
| **Modify Column** | `modify column_name:new_type` | Changes column data type | ⚠️ Manual (requires original type) |
| **Rename Column** | `rename old_name:new_name` | Renames a column | ✅ Automatic (renames back) |

### Rollback Behavior

- **✅ Automatic Rollback**: Operations that can be automatically reversed
- **⚠️ Manual Rollback**: Operations that require manual intervention

**Example Migration:**
```python
def up(self):
    return """
    ALTER TABLE users ADD COLUMN age INTEGER;
    ALTER TABLE users DROP COLUMN old_column;
    ALTER TABLE users RENAME COLUMN product_name TO name;
    """

def down(self):
    return """
    ALTER TABLE users DROP COLUMN age;
    -- ALTER TABLE users ADD COLUMN old_column <original_type>; -- Manual rollback required
    ALTER TABLE users RENAME COLUMN name TO product_name;
    """
```

### Best Practices

1. **Test rollbacks** before applying to production
2. **Document manual rollbacks** for complex operations
3. **Use transactions** for multiple operations
4. **Backup data** before destructive operations

---

## 📝 Column Definition Syntax

When creating migrations, you can specify columns using the format: `column_name:data_type`

### Examples:
```bash
# Basic types
john-migrator create users name:varchar(255) age:integer

# With constraints
john-migrator create posts title:varchar(255) content:text author_id:integer

# Boolean and other types
john-migrator create settings user_id:integer is_active:boolean created_at:timestamp
```

### Supported Data Types:
- `varchar(n)` - Variable length string
- `text` - Long text
- `integer` - Integer number
- `bigint` - Large integer
- `decimal(p,s)` - Decimal number with precision
- `boolean` - True/False
- `timestamp` - Date and time
- `date` - Date only
- `json` - JSON data
- `uuid` - UUID/GUID

### Default Behavior:
- If no columns are specified, a default `name VARCHAR(255)` column is added
- If a column is specified without a type (e.g., `name`), it defaults to `VARCHAR(255)`
- All tables automatically get `id SERIAL PRIMARY KEY`, `created_at`, and `updated_at` columns

---

## 📁 Project Structure

After installation, your project structure will look like:

```
your-project/
├── john_migrator_config.py    # Database configuration
├── migrations/                # Your migration files
│   ├── m_20250101120000_create_users_table.py
│   └── m_20250101120001_add_user_profile.py
├── models/                    # Generated ORM models
│   ├── users.py
│   └── products.py
└── .env                       # Optional: environment variables
```

---

## 🔧 Configuration Options

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| `DB_USER` | `DB_USER` | `default_user` | Database username |
| `DB_PASSWORD` | `DB_PASSWORD` | `default_password` | Database password |
| `DB_HOST` | `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `DB_PORT` | `5432` | Database port |
| `DB_NAME` | `DB_NAME` | `default_db` | Database name |
| `MIGRATION_FOLDER` | `MIGRATION_FOLDER` | `./migrations` | Migration files location |
| `MIGRATION_TABLE` | `MIGRATION_TABLE` | `migrations` | Migration tracking table |
| `MODELS_FOLDER` | `MODELS_FOLDER` | `./models` | ORM model files location |
| `GENERATE_ORM_MODELS` | `GENERATE_ORM_MODELS` | `True` | Enable/disable ORM model generation |
| `ORM_BASE_CLASS` | `ORM_BASE_CLASS` | `Base` | SQLAlchemy base class name |

---

## 🧪 Development

### Testing Different Python Versions

To test compatibility with different Python versions, you can use:

```bash
# Using pyenv (recommended)
pyenv install 3.7.17
pyenv install 3.8.18
pyenv install 3.9.18
pyenv install 3.10.13
pyenv install 3.11.7
pyenv install 3.12.1

# Test each version
pyenv local 3.7.17 && python -m pip install -e .
pyenv local 3.8.18 && python -m pip install -e .
pyenv local 3.9.18 && python -m pip install -e .
pyenv local 3.10.13 && python -m pip install -e .
pyenv local 3.11.7 && python -m pip install -e .
pyenv local 3.12.1 && python -m pip install -e .
```

### Using Docker for Testing

```dockerfile
# Dockerfile for testing multiple Python versions
FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["john-migrator", "--help"]
```

---

## 📝 Migration Best Practices

1. **Always test migrations** in a development environment first
2. **Keep migrations small** and focused on a single change
3. **Use descriptive names** for your migration files
4. **Always implement both `up()` and `down()` methods**
5. **Use transactions** for complex migrations (handled automatically)
6. **Define columns when creating** to save time and reduce errors

---

Stay in control of your database schema with **DB Migrator**! ✨

