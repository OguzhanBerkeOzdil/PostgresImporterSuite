"""
Database Operations Module

This module handles all database operations including connection management,
schema creation, and data insertion.
"""

try:
    import psycopg2
    import pandas as pd
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
except ImportError as e:
    print(f"Required database modules not installed: {e}")
    print("Please install with: pip install -r requirements.txt")
    raise

import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

from .config import DatabaseConfig

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[Any] = None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        connection = None
        try:
            connection = psycopg2.connect(**self.config.get_connection_params())
            yield connection
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def create_schema_and_table(self) -> bool:
        """Create schema and table if they don't exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create schema
                create_schema_sql = f"""
                    CREATE SCHEMA IF NOT EXISTS {self.config.schema_name};
                """
                
                # Create table with improved structure
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.config.schema_name}.{self.config.table_name} (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        age INTEGER CHECK (age >= 0 AND age <= 150),
                        email VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """
                
                # Create index for email column
                create_index_sql = f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.config.table_name}_email 
                    ON {self.config.schema_name}.{self.config.table_name}(email);
                """
                
                # Create trigger for updated_at
                create_trigger_sql = f"""
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                    
                    DROP TRIGGER IF EXISTS update_{self.config.table_name}_updated_at 
                    ON {self.config.schema_name}.{self.config.table_name};
                    
                    CREATE TRIGGER update_{self.config.table_name}_updated_at 
                    BEFORE UPDATE ON {self.config.schema_name}.{self.config.table_name} 
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                """
                
                cursor.execute(create_schema_sql)
                cursor.execute(create_table_sql)
                cursor.execute(create_index_sql)
                cursor.execute(create_trigger_sql)
                
                conn.commit()
                logger.info("Schema and table created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error creating schema and table: {e}")
            return False
    
    def get_sqlalchemy_engine(self):
        """Get or create SQLAlchemy engine."""
        if self.engine is None:
            try:
                self.engine = create_engine(
                    self.config.get_sqlalchemy_url(),
                    pool_pre_ping=True,
                    pool_recycle=300
                )
            except Exception as e:
                logger.error(f"Error creating SQLAlchemy engine: {e}")
                raise
        return self.engine
    
    def insert_data(self, df: pd.DataFrame, if_exists: str = 'append') -> bool:
        """Insert data into the database table."""
        try:
            engine = self.get_sqlalchemy_engine()
            
            # Prepare data for insertion
            insert_df = df.copy()
            
            # Remove id column if it exists (let database generate it)
            if 'id' in insert_df.columns:
                insert_df = insert_df.drop('id', axis=1)
            
            # Ensure required columns exist
            required_columns = ['name', 'email']
            for col in required_columns:
                if col not in insert_df.columns:
                    logger.error(f"Required column '{col}' not found in data")
                    return False
            
            # Insert data using pandas to_sql with schema
            table_name = f"{self.config.schema_name}.{self.config.table_name}"
            
            with engine.connect() as conn:
                # Use raw SQL for better control
                if if_exists == 'replace':
                    # Clear existing data
                    conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY"))
                
                # Insert data row by row to handle conflicts
                success_count = 0
                for _, row in insert_df.iterrows():
                    try:
                        # Use ON CONFLICT to handle duplicate emails
                        insert_sql = f"""
                            INSERT INTO {table_name} (name, age, email)
                            VALUES (:name, :age, :email)
                            ON CONFLICT (email) DO UPDATE SET
                                name = EXCLUDED.name,
                                age = EXCLUDED.age,
                                updated_at = CURRENT_TIMESTAMP
                        """
                        
                        conn.execute(text(insert_sql), {
                            'name': row['name'],
                            'age': row.get('age', None),
                            'email': row['email']
                        })
                        success_count += 1
                        
                    except Exception as row_error:
                        logger.warning(f"Error inserting row {row.to_dict()}: {row_error}")
                        continue
                
                conn.commit()
                logger.info(f"Successfully inserted/updated {success_count} records")
                return success_count > 0
                
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get table information and statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get record count
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {self.config.schema_name}.{self.config.table_name}
                """)
                count = cursor.fetchone()[0]
                
                # Get table structure
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = '{self.config.schema_name}'
                    AND table_name = '{self.config.table_name}'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                
                return {
                    'record_count': count,
                    'columns': columns,
                    'schema': self.config.schema_name,
                    'table': self.config.table_name
                }
                
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {}
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
