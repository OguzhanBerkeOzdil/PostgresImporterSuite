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
    
    SUPPORTED_FORMATS = ['csv', 'xlsx', 'xls', 'json', 'txt', 'tsv']
    
    # Additional format mappings for extensibility
    FORMAT_EXTENSIONS = {
        '.csv': 'csv',
        '.xlsx': 'xlsx',
        '.xls': 'xlsx', 
        '.json': 'json',
        '.txt': 'txt',
        '.tsv': 'tsv',
        '.tab': 'tsv'
    }
    
    @staticmethod
    def get_file_format(file_path: Union[str, Path]) -> str:
        """Detect file format from extension."""
        ext = os.path.splitext(str(file_path))[1].lower()
        return DataProcessor.FORMAT_EXTENSIONS.get(ext, 'unknown')
    
    @staticmethod
    def validate_file_exists(file_path: Union[str, Path]) -> bool:
        """Validate if file exists."""
        return os.path.isfile(file_path)
    
    @staticmethod
    def read_csv_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Read CSV file and return DataFrame."""
        try:
            # Try different encodings and separators
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            separators = [',', ';', '\t']
            
            df = None
            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if len(df.columns) > 1:  # Valid if more than 1 column
                            break
                    except:
                        continue
                if df is not None and len(df.columns) > 1:
                    break
            
            # If no valid DataFrame found, try fallback
            if df is None or len(df.columns) <= 1:
                df = pd.read_csv(file_path)
            
            # Handle files without proper headers
            if df.empty:
                # Try reading without header
                df = pd.read_csv(file_path, header=None)
                df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
            elif all(str(col).startswith('Unnamed:') or str(col).isdigit() for col in df.columns):
                # Generate better column names
                df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
            
            # Clean column names (remove spaces and special characters)
            df.columns = df.columns.astype(str).str.strip()
            df.columns = [col.replace(' ', '_').replace('-', '_') for col in df.columns]
            
            return df
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise
    
    @staticmethod
    def read_tsv_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Read TSV (Tab-separated values) file."""
        try:
            df = pd.read_csv(file_path, sep='\t')
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            logger.error(f"Error reading TSV file {file_path}: {e}")
            raise
    
    @staticmethod
    def read_txt_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Read text file with auto-detection of delimiter."""
        try:
            # Try common delimiters
            delimiters = ['\t', ',', ';', '|', ' ']
            
            for delimiter in delimiters:
                try:
                    df = pd.read_csv(file_path, sep=delimiter)
                    if len(df.columns) > 1:
                        df.columns = df.columns.str.strip()
                        return df
                except:
                    continue
            
            # If no delimiter works, read as single column
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            df = pd.DataFrame({'data': [line.strip() for line in lines if line.strip()]})
            return df
            
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            raise
    
    @staticmethod
    def read_excel_file(file_path: Union[str, Path]) -> pd.DataFrame:
        """Read Excel file and return DataFrame."""
        try:
            # Try reading as Excel first, then as CSV if fails
            try:
                # Try reading with header first
                df = pd.read_excel(file_path, engine='openpyxl')
                
                # Check if the first row contains only numbers (likely data, not headers)
                if not df.empty and len(df.columns) > 0:
                    first_row_all_numeric = all(
                        pd.api.types.is_numeric_dtype(df[col]) and 
                        not pd.isna(df[col].iloc[0]) if len(df) > 0 else False
                        for col in df.columns
                    )
                    
                    # Check if column names are numeric or unnamed
                    cols_are_numeric_or_unnamed = all(
                        str(col).startswith('Unnamed:') or 
                        str(col).replace('.', '').isdigit() 
                        for col in df.columns
                    )
                    
                    if cols_are_numeric_or_unnamed or first_row_all_numeric:
                        # Re-read without header
                        df = pd.read_excel(file_path, engine='openpyxl', header=None)
                        # Generate proper column names
                        df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
                
                # If still empty, try reading without header
                if df.empty:
                    df = pd.read_excel(file_path, engine='openpyxl', header=None)
                    df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
                
            except Exception:
                # If Excel reading fails, try as CSV (for mock files)
                try:
                    df = pd.read_csv(file_path)
                    # Same logic for CSV
                    if not df.empty and len(df.columns) > 0:
                        cols_are_numeric_or_unnamed = all(
                            str(col).startswith('Unnamed:') or 
                            str(col).replace('.', '').isdigit() 
                            for col in df.columns
                        )
                        
                        if cols_are_numeric_or_unnamed:
                            df = pd.read_csv(file_path, header=None)
                            df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
                except Exception:
                    # Final fallback: read as CSV without header
                    df = pd.read_csv(file_path, header=None)
                    df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
            
            # Clean column names (remove spaces and special characters)
            df.columns = df.columns.astype(str).str.strip()
            df.columns = [col.replace(' ', '_').replace('-', '_') for col in df.columns]
            
            # Ensure we have at least some data
            if df.empty:
                raise ValueError("File appears to be empty or unreadable")
            
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
        """Read data file based on format and return clean DataFrame."""
        if not cls.validate_file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_format.lower() not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        # Read the file based on format
        if file_format.lower() == 'csv':
            df = cls.read_csv_file(file_path)
        elif file_format.lower() == 'xlsx':
            df = cls.read_excel_file(file_path)
        elif file_format.lower() == 'json':
            df = cls.read_json_file(file_path)
        elif file_format.lower() == 'tsv':
            df = cls.read_tsv_file(file_path)
        elif file_format.lower() == 'txt':
            df = cls.read_txt_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        # Clean and prepare the data dynamically
        return cls.prepare_data_for_import(df)
    
    @staticmethod
    def auto_detect_and_read(file_path: Union[str, Path]) -> pd.DataFrame:
        """Auto-detect file format and read data."""
        try:
            processor = DataProcessor()
            file_format = processor.get_file_format(file_path)
            return processor.read_data_file(file_path, file_format)
        except Exception as e:
            logger.error(f"Error auto-detecting and reading file {file_path}: {e}")
            raise
    
    @staticmethod
    def validate_data_structure(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate if DataFrame contains required columns."""
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.warning(f"Missing columns: {missing_columns}")
            return False
        return True
    
    @staticmethod
    def prepare_data_for_import(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for dynamic import - clean and optimize."""
        # Remove any rows with all NaN values
        df = df.dropna(how='all')
        
        # Remove any completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Clean column names - remove special characters, spaces
        new_columns = []
        for col in df.columns:
            clean_col = str(col).strip()
            if clean_col == '':
                clean_col = f'column_{len(new_columns)}'
            new_columns.append(clean_col)
        
        df.columns = new_columns
        
        # Convert object columns to string to avoid mixed types
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
                # Replace 'nan' string with None
                df[col] = df[col].replace('nan', None)
        
        return df
    
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
