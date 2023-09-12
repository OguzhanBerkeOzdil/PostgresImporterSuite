# PostgresImporterSuite

This project demonstrates how to integrate data from various file formats (CSV, Excel, and JSON) into a PostgreSQL database using Python and the psycopg2 and pandas libraries. It also creates a schema and table within the database for storing the data.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed
- PostgreSQL database installed and running
- Required Python libraries installed (psycopg2, pandas, sqlalchemy)

## Getting Started

1. Clone this repository to your local machine:
   git clone https://github.com/OguzhanBerkeOzdil/PostgresImporterSuite.git

2. Install the required Python libraries if not already installed:
   pip install psycopg2 pandas sqlalchemy

3. Configure your PostgreSQL database connection details in the code:
   database_name = "YourDatabaseName"
   host = "localhost"
   user = "YourUsername"
   password = "YourPassword"
   
## Usage
Place your data files in the project directory with the following extensions (There is an example of each of the 3 files in the project file):
  CSV:   data.csv
  Excel: data.xlsx
  JSON:  data.json
  
The script will read the data file and store it in the specified database table.

## Database Structure
The script creates a schema named my_schema and a table named my_table in the PostgreSQL database. The table has the following columns:

+id (Serial Primary Key)
+name (VARCHAR)
+age (INT)
+email (VARCHAR)
