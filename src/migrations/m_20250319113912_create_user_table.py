from src.database.base_migration import BaseMigration

class CreateUserTable(BaseMigration):
    def __init__(self):
        self.table_name = "create_user_table"

    def up(self):
        return """
        CREATE TABLE create_user_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """

    def down(self):
        return f'DROP TABLE IF EXISTS "create_user_table";'
