"""
Create Excel file from CSV data (without pandas dependency)
"""

import csv
import json

def create_mock_excel_data():
    """Create Excel data structure without using pandas/openpyxl"""
    data = [
        {"id": 1, "name": "Sarah Connor", "age": 45, "email": "sarah@example.com"},
        {"id": 2, "name": "John Connor", "age": 25, "email": "john.connor@example.com"},
        {"id": 3, "name": "Kyle Reese", "age": 35, "email": "kyle@example.com"},
        {"id": 4, "name": "Ellen Ripley", "age": 40, "email": "ripley@example.com"},
        {"id": 5, "name": "Dutch Schaefer", "age": 42, "email": "dutch@example.com"}
    ]
    return data

# Since we can't create real Excel files without openpyxl, 
# let's create a JSON file that simulates Excel data structure
if __name__ == "__main__":
    data = create_mock_excel_data()
    
    # Save as JSON (can be read by data_utils.py)
    with open("data/excel_as_json.json", "w") as f:
        json.dump({"data": data}, f, indent=2)
    
    print("Mock Excel data created as JSON file")
