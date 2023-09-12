import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import json
import os

# Define database connection parameters
database_name = "YourDatabaseName"
host = "YourHostName"
user = "YourUsername"
password = "YourPassword"


try: # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        database=database_name,
        host=host,
        user=user,
        password=password
    )
    cursor = connection.cursor()
    print("Connected to the database!")


    create_schema_sql = """
        CREATE SCHEMA IF NOT EXISTS my_schema;
        """

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS my_schema.my_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            age INT,
            email VARCHAR(255)
        );
        """

    cursor.execute(create_schema_sql)
    cursor.execute(create_table_sql)

    print("Select the file type you want to store:")
    print("1. CSV")
    print("2. Excel")
    print("3. JSON")

    choice = input("Enter the corresponding number: ")

    # Determine the file extension based on user input
    if choice == '1':
        file_extension = 'csv'
    elif choice == '2':
        file_extension = 'xlsx'
    elif choice == '3':
        file_extension = 'json'
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
        exit()

    data_file_path = f'data.{file_extension}'

    # Read data from the selected file type
    if os.path.isfile(data_file_path):
        if file_extension == 'csv':
            data = pd.read_csv(data_file_path)
        elif file_extension == 'xlsx':
            data = pd.read_excel(data_file_path)
        elif file_extension == 'json':
            with open(data_file_path, 'r') as json_file:
                json_data = json.load(json_file)
                data_list = json_data.get("people", [])
                data = pd.DataFrame(data_list)
    else:
        print(f"No {file_extension} data file found at the specified location.")
        exit()

    # Create a SQLAlchemy engine for database interaction
    engine = create_engine(f'postgresql://{user}:{password}@{host}/{database_name}')

    # Write the data to the PostgreSQL table
    data.to_sql('my_table', engine, if_exists='replace', index=False)

    # Commit the changes to the database
    connection.commit()

except psycopg2.Error as notConnection:
    print(f"Error connecting to the database or executing SQL queries: {notConnection}")
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Database connection is successful, the connection is closed.")
