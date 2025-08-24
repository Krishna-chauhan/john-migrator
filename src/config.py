import os
import importlib.util
from dotenv import load_dotenv


class Config:
    def __init__(self, config_file="john_migrator_config.py", env_file=".env"):
        # Load environment variables from .env if available
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"Loaded environment variables from {env_file}")
        else:
            print("No .env file found. Using defaults or user config.")

        # Attempt to load user config
        self.load_user_config(config_file)

        # Set defaults if not provided
        self.DB_USER = getattr(self, "DB_USER", os.getenv("DB_USER", "default_user"))
        self.DB_PASSWORD = getattr(self, "DB_PASSWORD", os.getenv("DB_PASSWORD", "default_password"))
        self.DB_HOST = getattr(self, "DB_HOST", os.getenv("DB_HOST", "localhost"))
        self.DB_PORT = getattr(self, "DB_PORT", os.getenv("DB_PORT", "5432"))
        self.DB_NAME = getattr(self, "DB_NAME", os.getenv("DB_NAME", "default_db"))
        
        # Use current working directory for migrations by default
        default_migration_folder = os.path.join(os.getcwd(), "migrations")
        self.MIGRATION_FOLDER = getattr(self, "MIGRATION_FOLDER", os.getenv("MIGRATION_FOLDER", default_migration_folder))
        self.MIGRATION_TABLE = getattr(self, "MIGRATION_TABLE", os.getenv("MIGRATION_TABLE", "migrations"))

        self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def load_user_config(self, config_file):
        if os.path.exists(config_file):
            spec = importlib.util.spec_from_file_location("user_config", config_file)
            user_config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_config)

            # Dynamically load user config
            for attr in dir(user_config):
                if attr.isupper():
                    setattr(self, attr, getattr(user_config, attr))
            print(f"User config loaded from {config_file}")
        else:
            print(f"No user config found at {config_file}. Using defaults or environment variables.")

    def __str__(self):
        return (f"Database URL: {self.DATABASE_URL}\n"
                f"Migration Folder: {self.MIGRATION_FOLDER}\n"
                f"Migration Table: {self.MIGRATION_TABLE}")
