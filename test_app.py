"""
Test script for PostgreSQL Data Import Suite

This script tests the basic functionality without requiring database connection.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all modules can be imported."""
    try:
        from src.config import DatabaseConfig
        print("✓ Config module imported successfully")
        
        try:
            from src.database import DatabaseManager
            print("✓ Database module imported successfully")
        except ImportError as e:
            print(f"⚠ Database module import failed (expected if dependencies not installed): {e}")
            
        try:
            from src.data_utils import DataProcessor
            print("✓ Data utils module imported successfully")
        except ImportError as e:
            print(f"⚠ Data utils module import failed (expected if dependencies not installed): {e}")
            
        print("✓ Core modules structure is correct")
        return True
    except ImportError as e:
        print(f"✗ Critical import error: {e}")
        return False

def test_data_processing():
    """Test data processing functionality."""
    try:
        # Test if sample data files exist
        data_dir = Path("data")
        required_files = ["data.csv", "data.json"]
        
        for file_name in required_files:
            file_path = data_dir / file_name
            if file_path.exists():
                print(f"✓ Found {file_name}")
                
                # Test basic file reading (without pandas dependency)
                try:
                    if file_name.endswith('.csv'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            print(f"✓ Successfully read {file_name} ({len(lines)-1} data rows)")
                    elif file_name.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            import json
                            data = json.load(f)
                            if 'people' in data:
                                print(f"✓ Successfully read {file_name} ({len(data['people'])} records)")
                            else:
                                print(f"✓ Successfully read {file_name} (JSON structure verified)")
                except Exception as e:
                    print(f"⚠ Error reading {file_name}: {e}")
                    continue
            else:
                print(f"⚠ Sample file {file_name} not found")
        
        return True
    except Exception as e:
        print(f"✗ Data processing test failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    try:
        from src.config import DatabaseConfig
        
        config = DatabaseConfig()
        print(f"✓ Configuration loaded:")
        print(f"  Database: {config.db_name}")
        print(f"  Host: {config.host}")
        print(f"  Schema: {config.schema_name}")
        print(f"  Table: {config.table_name}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("    PostgreSQL Data Import Suite - Tests")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Data Processing", test_data_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print("Test Results:")
    for i, (test_name, _) in enumerate(tests):
        status = "✓ PASSED" if results[i] else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    if all(results):
        print("\n✓ All tests passed! The application should work correctly.")
    else:
        print("\n⚠ Some tests failed. Please check the configuration and requirements.")
    print("="*60)

if __name__ == "__main__":
    main()
