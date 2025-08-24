from john_migrator.migrations.base_migration import BaseMigration


class UserTable(BaseMigration):
    def __init__(self):
        self.table_name = "user_table"

    def up(self):
        return """
        CREATE TABLE user_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """

    def down(self):
        return f'DROP TABLE IF EXISTS "user_table";'
