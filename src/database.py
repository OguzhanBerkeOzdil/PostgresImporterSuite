"""
Database Operations Module

This module handles all database operations including connection management,
schema creation, and data insertion with dynamic table support.

Author: Oğuzhan Berke Özdil
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
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from .config import DatabaseConfig

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database operations manager with dynamic table support."""
    
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
    
    def create_dynamic_table(self, df: pd.DataFrame, table_name: Optional[str] = None) -> bool:
        """Create table dynamically based on DataFrame structure."""
        try:
            if table_name is None:
                table_name = self.config.table_name
                
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create schema
                create_schema_sql = f"CREATE SCHEMA IF NOT EXISTS {self.config.schema_name};"
                cursor.execute(create_schema_sql)
                
                # Generate column definitions based on DataFrame
                columns = []
                for col_name, dtype in df.dtypes.items():
                    # Clean column name (remove special characters, spaces)
                    clean_col = str(col_name).strip().replace(' ', '_').replace('-', '_').lower()
                    clean_col = ''.join(c for c in clean_col if c.isalnum() or c == '_')
                    
                    if clean_col == '' or clean_col[0].isdigit():
                        clean_col = f"col_{clean_col}"
                    
                    # Determine SQL type based on pandas dtype
                    if pd.api.types.is_integer_dtype(dtype):
                        sql_type = "INTEGER"
                    elif pd.api.types.is_float_dtype(dtype):
                        sql_type = "DECIMAL"
                    elif pd.api.types.is_datetime64_any_dtype(dtype):
                        sql_type = "TIMESTAMP"
                    else:
                        sql_type = "TEXT"
                    
                    columns.append(f"{clean_col} {sql_type}")
                
                # Add auto-increment ID column if not exists
                if not any('id' in col.lower() for col in columns):
                    columns.insert(0, "auto_id SERIAL PRIMARY KEY")
                
                # Add metadata columns
                columns.append("imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                
                # Drop existing table if exists (for dynamic updates)
                drop_table_sql = f"DROP TABLE IF EXISTS {self.config.schema_name}.{table_name};"
                cursor.execute(drop_table_sql)
                
                # Create new table
                create_table_sql = f"""
                    CREATE TABLE {self.config.schema_name}.{table_name} (
                        {', '.join(columns)}
                    );
                """
                
                cursor.execute(create_table_sql)
                conn.commit()
                
                logger.info(f"Dynamic table created: {self.config.schema_name}.{table_name}")
                logger.info(f"Columns: {columns}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating dynamic table: {e}")
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
    
    def insert_dynamic_data(self, df: pd.DataFrame, table_name: Optional[str] = None) -> bool:
        """Insert data dynamically into database table."""
        try:
            if table_name is None:
                table_name = self.config.table_name
                
            # First create the table based on DataFrame structure
            if not self.create_dynamic_table(df, table_name):
                return False
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare data for insertion
                insert_df = df.copy()
                
                # Clean column names to match table structure
                column_mapping = {}
                for col in insert_df.columns:
                    clean_col = col.strip().replace(' ', '_').replace('-', '_').lower()
                    clean_col = ''.join(c for c in clean_col if c.isalnum() or c == '_')
                    if clean_col == '' or clean_col[0].isdigit():
                        clean_col = f"col_{clean_col}"
                    column_mapping[col] = clean_col
                
                insert_df = insert_df.rename(columns=column_mapping)
                
                # Insert data row by row
                success_count = 0
                for _, row in insert_df.iterrows():
                    try:
                        # Create column list and value placeholders
                        columns = list(insert_df.columns)
                        placeholders = ', '.join(['%s'] * len(columns))
                        column_names = ', '.join(columns)
                        
                        insert_sql = f"""
                            INSERT INTO {self.config.schema_name}.{table_name} ({column_names})
                            VALUES ({placeholders})
                        """
                        
                        # Convert row to list, replacing NaN with None
                        values = [None if pd.isna(val) else val for val in row.values]
                        
                        cursor.execute(insert_sql, values)
                        success_count += 1
                        
                    except Exception as row_error:
                        logger.warning(f"Error inserting row: {row_error}")
                        continue
                
                conn.commit()
                logger.info(f"Successfully inserted {success_count} records into {table_name}")
                return success_count > 0
                
        except Exception as e:
            logger.error(f"Error inserting dynamic data: {e}")
            return False
    
    def get_table_info(self, table_name: Optional[str] = None) -> Dict[str, Any]:
        """Get table information and statistics."""
        try:
            if table_name is None:
                table_name = self.config.table_name
                
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if table exists
                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = %s AND table_name = %s
                    );
                """, (self.config.schema_name, table_name))
                
                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    return {"exists": False}
                
                # Get record count
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {self.config.schema_name}.{table_name}
                """)
                count = cursor.fetchone()[0]
                
                # Get table structure
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;
                """, (self.config.schema_name, table_name))
                
                columns = cursor.fetchall()
                
                return {
                    "exists": True,
                    "record_count": count,
                    "columns": [{"name": col[0], "type": col[1]} for col in columns]
                }
                
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {"exists": False, "error": str(e)}
    
    def get_sample_data(self, table_name: Optional[str] = None, limit: int = 50) -> Optional[pd.DataFrame]:
        """Get sample data from table with latest records first."""
        try:
            if table_name is None:
                table_name = self.config.table_name
                
            # Force fresh connection by disposing old engine
            if self.engine:
                self.engine.dispose()
                self.engine = None
            
            engine = self.get_sqlalchemy_engine()
            
            # Try to get the most recent data first
            try:
                # Check if imported_at column exists
                check_column_sql = f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = '{self.config.schema_name}' 
                    AND table_name = '{table_name}' 
                    AND column_name = 'imported_at'
                """
                
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(check_column_sql)
                    has_imported_at = cursor.fetchone() is not None
                
                if has_imported_at:
                    sql = f"SELECT * FROM {self.config.schema_name}.{table_name} ORDER BY imported_at DESC LIMIT {limit}"
                else:
                    # Try to order by any ID-like column, or just get data
                    try:
                        # Get column info to find a good ordering column
                        with self.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute(f"""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_schema = '{self.config.schema_name}' 
                                AND table_name = '{table_name}' 
                                AND (column_name ILIKE '%id%' OR column_name = 'auto_id')
                                ORDER BY ordinal_position
                                LIMIT 1
                            """)
                            id_column = cursor.fetchone()
                            
                        if id_column:
                            sql = f"SELECT * FROM {self.config.schema_name}.{table_name} ORDER BY {id_column[0]} DESC LIMIT {limit}"
                        else:
                            sql = f"SELECT * FROM {self.config.schema_name}.{table_name} LIMIT {limit}"
                    except Exception:
                        sql = f"SELECT * FROM {self.config.schema_name}.{table_name} LIMIT {limit}"
                    
            except Exception:
                # Fallback if table info check fails
                sql = f"SELECT * FROM {self.config.schema_name}.{table_name} LIMIT {limit}"
            
            logger.info(f"Executing query: {sql}")
            df = pd.read_sql(sql, engine)
            
            logger.info(f"Retrieved {len(df)} rows from {self.config.schema_name}.{table_name}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting sample data from {table_name}: {e}")
            return None
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in the schema."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    ORDER BY table_name
                """, (self.config.schema_name,))
                
                tables = [row[0] for row in cursor.fetchall()]
                return tables
                
        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            return []
