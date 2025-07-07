"""
Create a mock Excel file as CSV since we don't have openpyxl installed yet
This will be used for testing Excel functionality
"""

csv_content = """id,name,age,email
1,Sarah Connor,45,sarah@example.com
2,John Connor,25,john.connor@example.com
3,Kyle Reese,35,kyle@example.com
4,Ellen Ripley,40,ripley@example.com
5,Dutch Schaefer,42,dutch@example.com"""

# Write as .xlsx file (even though it's CSV format)
# Our data_utils.py will handle this appropriately
with open("data/data.xlsx", "w") as f:
    f.write(csv_content)

print("Mock Excel file created (as CSV format)")
