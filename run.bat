@echo off
echo ================================
echo PostgreSQL Data Import Suite
echo ================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Running setup...
    python setup.py
    echo.
    echo Setup completed. Please update .env file with your database credentials.
    echo Then run this script again.
    pause
    exit /b
)

REM Activate virtual environment and run application
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting application...
python main.py

echo.
echo Application finished.
pause
