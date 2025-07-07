"""
PostgreSQL Data Import Suite

A modern Python application for importing data from various file formats 
(CSV, Excel, JSON) into PostgreSQL database with proper error handling,
logging, and configuration management.

Author: Oğuzhan Berke Özdil
Updated: 2025
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import DatabaseConfig
    from src.database import DatabaseManager
    from src.data_utils import DataProcessor
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure you have installed the required packages:")
    print("pip install -r requirements.txt")
    print("\nOr run the setup script first:")
    print("python setup.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_log.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DataImportApp:
    """Main application class for data import operations."""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.db_manager = DatabaseManager(self.config)
        self.data_processor = DataProcessor()
        
    def display_menu(self) -> None:
        """Display the application menu."""
        print("\n" + "="*60)
        print("         PostgreSQL Data Import Suite")
        print("="*60)
        print("Select the file type you want to import:")
        print("1. CSV File (data.csv)")
        print("2. Excel File (data.xlsx)")
        print("3. JSON File (data.json)")
        print("4. Show Database Info")
        print("5. Test Database Connection")
        print("0. Exit")
        print("="*60)
    
    def get_user_choice(self) -> str:
        """Get and validate user input."""
        while True:
            choice = input("Enter your choice (0-5): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5']:
                return choice
            print("Invalid choice. Please enter a number between 0-5.")
    
    def get_file_format(self, choice: str) -> Optional[str]:
        """Convert user choice to file format."""
        format_map = {
            '1': 'csv',
            '2': 'xlsx',
            '3': 'json'
        }
        return format_map.get(choice)
    
    def test_database_connection(self) -> bool:
        """Test database connection."""
        print("\nTesting database connection...")
        try:
            if self.db_manager.test_connection():
                print("✓ Database connection successful!")
                return True
            else:
                print("✗ Database connection failed!")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def show_database_info(self) -> None:
        """Display database information."""
        print("\nRetrieving database information...")
        try:
            info = self.db_manager.get_table_info()
            if info:
                print(f"\nDatabase Information:")
                print(f"Schema: {info['schema']}")
                print(f"Table: {info['table']}")
                print(f"Record Count: {info['record_count']}")
                print(f"\nTable Structure:")
                for col in info['columns']:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    default = f"DEFAULT {col[3]}" if col[3] else ""
                    print(f"  {col[0]} ({col[1]}) {nullable} {default}")
            else:
                print("Could not retrieve database information.")
        except Exception as e:
            print(f"Error retrieving database info: {e}")
    
    def import_data(self, file_format: str) -> bool:
        """Import data from specified file format."""
        try:
            # Determine file path
            data_directory = Path("data")
            if data_directory.exists():
                file_path = data_directory / f"data.{file_format}"
            else:
                file_path = Path(f"data.{file_format}")
            
            print(f"\nImporting data from {file_path}...")
            
            # Read data
            df = self.data_processor.read_data_file(file_path, file_format)
            print(f"✓ Successfully read {len(df)} records from {file_format.upper()} file")
            
            # Validate data structure
            required_columns = ['name', 'email']
            if not self.data_processor.validate_data_structure(df, required_columns):
                print("✗ Data validation failed: Missing required columns")
                return False
            
            # Clean data
            cleaned_df = self.data_processor.clean_data(df)
            print(f"✓ Data cleaned. {len(cleaned_df)} records ready for import")
            
            # Create schema and table
            print("Creating database schema and table...")
            if not self.db_manager.create_schema_and_table():
                print("✗ Failed to create database schema/table")
                return False
            print("✓ Database schema and table ready")
            
            # Insert data
            print("Inserting data into database...")
            if self.db_manager.insert_data(cleaned_df, if_exists='append'):
                print("✓ Data import completed successfully!")
                
                # Show summary
                info = self.db_manager.get_table_info()
                if info:
                    print(f"Total records in database: {info['record_count']}")
                return True
            else:
                print("✗ Data import failed")
                return False
                
        except FileNotFoundError:
            print(f"✗ File not found: data.{file_format}")
            print("Please ensure the data file exists in the current directory or 'data' folder")
            return False
        except Exception as e:
            logger.error(f"Import error: {e}")
            print(f"✗ Import failed: {e}")
            return False
    
    def run(self) -> None:
        """Run the main application."""
        print("Starting PostgreSQL Data Import Suite...")
        
        # Test initial connection
        if not self.test_database_connection():
            print("\nPlease check your database configuration in .env file")
            print("Copy .env.example to .env and update with your database details")
            return
        
        try:
            while True:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice == '0':
                    print("\nExiting application. Goodbye!")
                    break
                elif choice in ['1', '2', '3']:
                    file_format = self.get_file_format(choice)
                    self.import_data(file_format)
                elif choice == '4':
                    self.show_database_info()
                elif choice == '5':
                    self.test_database_connection()
                
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user. Exiting...")
        except Exception as e:
            logger.error(f"Application error: {e}")
            print(f"An unexpected error occurred: {e}")
        finally:
            # Cleanup
            self.db_manager.close()
            print("Database connections closed.")

def main():
    """Main entry point."""
    app = DataImportApp()
    app.run()

if __name__ == "__main__":
    main()
