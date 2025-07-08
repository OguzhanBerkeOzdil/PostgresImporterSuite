"""
Database Configuration Module

This module handles database connection configuration using environment variables.
"""

import os
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Environment variables from system will be used.")
    # Define a dummy function that does nothing
    pass

class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        self.db_name = os.getenv('DB_NAME', 'postgres')
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.schema_name = os.getenv('SCHEMA_NAME', 'data_import_schema')
        self.table_name = os.getenv('TABLE_NAME', 'imported_data')
    
    def load_from_env(self, env_file: str = '.env'):
        """Load configuration from environment file."""
        if os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            self.db_name = os.getenv('DB_NAME', self.db_name)
            self.host = os.getenv('DB_HOST', self.host)
            self.user = os.getenv('DB_USER', self.user)
            self.password = os.getenv('DB_PASSWORD', self.password)
            self.port = int(os.getenv('DB_PORT', str(self.port)))
            self.schema_name = os.getenv('SCHEMA_NAME', self.schema_name)
            self.table_name = os.getenv('TABLE_NAME', self.table_name)
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get database connection parameters."""
        return {
            'database': self.db_name,
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'port': self.port
        }
    
    def get_sqlalchemy_url(self) -> str:
        """Get SQLAlchemy database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
