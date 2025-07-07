# PostgreSQL Data Import Suite

## Original Project (2022-2023)

This project was originally developed as part of the Database 2 course project for Computer Science department at AGH University of Krakow, 2nd year.

**Original Developers:** Oğuzhan Berke Özdil and Berkay Doruk

The original project demonstrated basic data integration from various file formats (CSV, Excel, JSON) into a PostgreSQL database using Python, psycopg2, and pandas libraries.

## Modern Version (2025)

This project has been completely modernized and restructured to be a professional, maintainable, and user-friendly application.

**Updated by:** Oğuzhan Berke Özdil

### New Features and Improvements

- **Modern Architecture:** Modular design with proper separation of concerns
- **Configuration Management:** Environment-based configuration with .env files
- **Enhanced Error Handling:** Comprehensive error handling and logging
- **Data Validation:** Robust data validation and cleaning processes
- **Database Management:** Advanced database operations with connection pooling
- **User Interface:** Interactive command-line interface with clear feedback
- **Type Safety:** Full type hints for better code quality
- **Documentation:** Comprehensive documentation and code comments
- **Automated Setup:** Setup script for easy installation and configuration
- **UPSERT Operations:** Conflict resolution for duplicate email addresses
- **Auto Schema Creation:** Automatic database schema and table creation
- **Cross-platform Support:** Windows, Linux, and macOS compatibility
- **Test Suite:** Comprehensive testing framework included

### Technical Improvements

- **Error Recovery:** Graceful handling of database connection failures
- **Data Normalization:** Automatic data structure standardization across formats
- **SQL Injection Prevention:** Parameterized queries for security
- **Connection Pooling:** Efficient database connection management
- **Logging System:** Detailed application and error logging
- **Virtual Environment:** Isolated dependency management

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database server
- Git (for cloning the repository)

### Installation and Setup

#### Option 1: Automatic Setup (Recommended)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/OguzhanBerkeOzdil/PostgresImporterSuite.git
   cd PostgresImporterSuite
   ```

2. **Run the setup script:**

   ```bash
   python setup.py
   ```

   This will automatically:
   - Create a virtual environment
   - Install all required dependencies
   - Set up configuration files

#### Option 2: Manual Setup

1. **Create virtual environment:**

   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**

   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Setup environment file:**

   Copy the example configuration:

   ```bash
   cp .env.example .env
   ```

2. **Configure database connection:**

   Update the `.env` file with your PostgreSQL credentials:

   ```env
   DB_NAME=your_database_name
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_PORT=5432
   ```

### Usage

1. **Activate virtual environment:**

   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Run the application:**

   ```bash
   python main.py
   ```

3. **Select operation from menu:**
   - 1: Import CSV file
   - 2: Import Excel file
   - 3: Import JSON file
   - 4: Show database information
   - 5: Test database connection
   - 0: Exit

### Data Files

Place your data files in the `data/` directory:

- **CSV:** `data/data.csv`
- **Excel:** `data/data.xlsx`
- **JSON:** `data/data.json`

Sample files are provided for testing.

### Database Structure

The application creates an enhanced database structure with the following schema:

**Schema:** `data_import_schema` (configurable via .env)  
**Table:** `imported_data` (configurable via .env)

**Table Structure:**
```sql
CREATE TABLE data_import_schema.imported_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_imported_data_email ON data_import_schema.imported_data(email);

-- Trigger for automatic timestamp updates
CREATE TRIGGER update_imported_data_updated_at 
BEFORE UPDATE ON data_import_schema.imported_data 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Key Improvements:**
- Email uniqueness constraint prevents duplicates
- Age validation ensures data quality
- Automatic timestamp management
- Optimized indexes for query performance
- UPSERT operations for conflict resolution

### Testing

To test the application without connecting to a database:

```bash
python test_app.py
```

This will verify that all modules are working correctly and sample data files can be processed.

### Troubleshooting

**Common Issues:**

1. **Database Connection Failed:**
   - Verify PostgreSQL is running
   - Check credentials in `.env` file
   - Ensure database exists and user has proper permissions

2. **Module Import Errors:**
   - Make sure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

3. **File Not Found Errors:**
   - Ensure data files are in the `data/` directory
   - Check file permissions

**Logging:**

Application logs are saved to `import_log.log` for debugging purposes.

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Version History

**Version 2.0 (2025)** - Complete modernization with modular architecture, enhanced error handling, UPSERT operations, and interactive CLI.

**Version 1.0 (2022-2023)** - Original university project for Database 2 course at AGH University of Krakow.
