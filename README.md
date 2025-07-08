# PostgreSQL Data Import Tool

A user-friendly GUI application for importing CSV, Excel, and JSON files into PostgreSQL databases with dynamic table creation.

## Project History

This project was originally started 3 years ago as a term project for the Database 2 course at **AGH University of Science and Technology**. The initial development team consisted of:

- **Oğuzhan Berke Özdil** (Bachelor Computer Science, 2nd year)
- **Berkay Doruk** (Bachelor Computer Science, 2nd year)

The project has since evolved and been completely rewritten and maintained by **Oğuzhan Berke Özdil**.

## Features

- **Dynamic Import**: Automatically handles any file structure and column names
- **Multiple Formats**: Supports CSV, Excel (.xlsx, .xls), and JSON files
- **Smart Preview**: Preview data before import, even for files without headers
- **Auto Table Creation**: Creates schemas and tables automatically based on data structure
- **Real-time Connection Testing**: Test database connectivity with visual feedback
- **Progress Tracking**: Live import progress with detailed status updates
- **Data Validation**: Handles missing headers, special characters, and various data types
- **Latest Data View**: View imported data with most recent records first

## Quick Start

1. **Run the Application**:
   ```bash
   PostgreSQL-Data-Import.exe
   ```

2. **Configure Database**:
   - Click "Database Settings"
   - Enter PostgreSQL connection details
   - Test connection (✅/❌ status shown)
   - Create schema/table if needed

3. **Import Data**:
   - Click "Browse Files" to select data files
   - Preview files to verify structure
   - Click "Import Data" to process
   - Monitor progress and status

4. **View Results**:
   - Click "View Database" to see imported data
   - Check sync status indicators

## Database Configuration

**Required Settings**:
- Host: PostgreSQL server address
- Port: Database port (default: 5432)
- Database: Target database name
- Username/Password: Database credentials
- Schema: Target schema (created if missing)
- Table: Base table name for imports

**Connection Features**:
- ✅ Real-time connection testing
- 🔧 Automatic schema/table creation
- 🔄 Sync status indicators
- 💾 Save settings to .env file

## File Support

**Supported Formats**:
- CSV files (any delimiter, encoding)
- Excel files (.xlsx, .xls)
- JSON files (various structures)

**Smart Handling**:
- Files without headers → Auto-generates column names
- Numeric-only data → Creates structured columns
- Special characters → Cleaned for database compatibility
- Mixed data types → Automatic type detection

## Import Process

1. **File Selection**: Choose one or multiple files
2. **Preview**: Check data structure and content
3. **Import**: Dynamic table creation and data insertion
4. **Validation**: Real-time progress and error handling
5. **Verification**: View imported data immediately

## Status Indicators

- 🔄 Connection testing in progress
- ✅ Connected and ready
- ❌ Connection failed
- ⚠️ Partial import success
- 🎉 Complete import success

## Technical Details

- **Language**: Python 3.13+
- **Database**: PostgreSQL with psycopg2 and SQLAlchemy
- **GUI**: Tkinter with modern styling
- **Data**: Pandas for processing and validation
- **Build**: PyInstaller for standalone executable

## Requirements

- Windows 10/11
- PostgreSQL database (local or remote)
- Valid database credentials

---

**Current Maintainer**: Oğuzhan Berke Özdil  
**Version**: 2.0 - Dynamic Import  
**License**: MIT

## Supported Data Formats

### CSV Files (.csv)
- Automatic delimiter detection (comma, semicolon, tab)
- Multiple encoding support (UTF-8, Latin-1, CP1252)
- Header row recognition

### Excel Files (.xlsx, .xls)
- Native Excel format support
- First worksheet import
- Mixed data type handling

### JSON Files (.json)
- Nested object flattening
- Array data extraction
- Flexible schema adaptation

## Database Operations

The application creates tables dynamically based on the imported file structure:

- **Column Names**: Cleaned and normalized from file headers
- **Data Types**: Automatically mapped (TEXT, INTEGER, DECIMAL, TIMESTAMP)
- **Primary Keys**: Auto-increment ID columns when needed
- **Metadata**: Import timestamp tracking
- **Schema Management**: Organized within configurable database schemas

## Configuration

Database settings are managed through the built-in configuration dialog:

- **Host**: Database server address
- **Port**: Connection port (default: 5432)
- **Database**: Target database name
- **Username**: Database user credentials
- **Password**: Secure password handling
- **Schema**: Target schema for table creation
- **Table**: Default table name (overridden by filename)

Settings can be saved to `.env` files for reuse across sessions.

## Development Build

For developers who need to build from source:

### Prerequisites
```bash
pip install -r requirements.txt
```

### Build Process
```bash
python build.py
```

The executable will be generated in the `dist/` directory.

### Dependencies
- pandas: Data manipulation and analysis
- psycopg2-binary: PostgreSQL database adapter
- sqlalchemy: Database toolkit and ORM
- openpyxl: Excel file processing
- python-dotenv: Environment variable management
- numpy: Numerical computing support

## Project Evolution

**Version 1.0**: Initial command-line implementation with basic import functionality  
**Version 2.0**: Complete GUI redesign with dynamic import capabilities and enhanced user experience

The tool has been designed for scalability and maintainability, with modular architecture supporting future enhancements and additional data formats.

---

**Oğuzhan Berke Özdil** - 2025
