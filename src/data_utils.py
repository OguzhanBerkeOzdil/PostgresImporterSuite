"""
Data Import Utilities

This module contains utility functions for data processing and validation.
"""

try:
    import pandas as pd
except ImportError as e:
    print(f"Pandas not installed: {e}")
    print("Please install with: pip install -r requirements.txt")
    raise

import json
import os
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class DataProcessor:
    """Data processing utilities for different file formats."""
    
    SUPPORTED_FORMATS = ['csv', 'xlsx', 'json']
    
    @staticmethod
    def validate_file_exists(file_path: Union[str, Path]) -> bool:
        """Validate if file exists."""
        return os.path.isfile(file_path)
    
    @staticmethod
    def read_csv_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Read CSV file and return DataFrame."""
        try:
            df = pd.read_csv(file_path)
            # Clean column names (remove spaces)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise
    
    @staticmethod
    def read_excel_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Read Excel file and return DataFrame."""
        try:
            # Try reading as Excel first, then as CSV if fails
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except Exception:
                # If Excel reading fails, try as CSV (for mock files)
                df = pd.read_csv(file_path)
            # Clean column names (remove spaces)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {e}")
            raise
    
    @staticmethod
    def read_json_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Read JSON file and return DataFrame."""
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)
                
                # Handle different JSON structures
                if isinstance(json_data, dict):
                    if 'people' in json_data:
                        data_list = json_data['people']
                    elif 'data' in json_data:
                        data_list = json_data['data']
                    else:
                        # Assume the dict values are the data
                        data_list = list(json_data.values())
                        if len(data_list) == 1 and isinstance(data_list[0], list):
                            data_list = data_list[0]
                elif isinstance(json_data, list):
                    data_list = json_data
                else:
                    raise ValueError("Unsupported JSON structure")
                
                df = pd.DataFrame(data_list)
                
                # Normalize JSON structure to match CSV/Excel format
                if 'firstName' in df.columns and 'lastName' in df.columns:
                    df['Name'] = df['firstName'] + ' ' + df['lastName']
                    df = df.drop(['firstName', 'lastName'], axis=1)
                
                # Standardize column names
                column_mapping = {
                    'Id': 'id',
                    'Name': 'name',
                    'Age': 'age',
                    'age': 'age',
                    'Email': 'email',
                    'email': 'email'
                }
                
                df = df.rename(columns=column_mapping)
                return df
                
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            raise
    
    @classmethod
    def read_data_file(cls, file_path: Union[str, Path], file_format: str) -> pd.DataFrame:
        """Read data file based on format."""
        if not cls.validate_file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_format.lower() not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        if file_format.lower() == 'csv':
            return cls.read_csv_file(file_path)
        elif file_format.lower() == 'xlsx':
            return cls.read_excel_file(file_path)
        elif file_format.lower() == 'json':
            return cls.read_json_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    @staticmethod
    def validate_data_structure(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate if DataFrame contains required columns."""
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")
            return False
        return True
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for database insertion."""
        # Remove any rows with all NaN values
        df = df.dropna(how='all')
        
        # Convert data types
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce')
        
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
        
        # Remove duplicates based on email if email column exists
        if 'email' in df.columns:
            df = df.drop_duplicates(subset=['email'], keep='first')
        
        return df
