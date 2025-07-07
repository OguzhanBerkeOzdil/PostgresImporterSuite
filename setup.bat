@echo off
REM PostgreSQL Data Import Suite - Setup Script (Windows)

echo ======================================================
echo     PostgreSQL Data Import Suite - Setup
echo ======================================================

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo X Failed to create virtual environment
    pause
    exit /b 1
)
echo √ Virtual environment created successfully

REM Activate virtual environment and install requirements
echo Installing required packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo X Failed to install requirements
    pause
    exit /b 1
)
echo √ Requirements installed successfully

REM Setup environment file
if not exist ".env" (
    if exist ".env.example" (
        echo Setting up environment configuration...
        copy ".env.example" ".env"
        echo √ Environment file created from template
        echo ! Please update .env file with your database credentials
    ) else (
        echo X No environment template found
    )
) else (
    echo √ Environment file already exists
)

echo.
echo ======================================================
echo √ Setup completed successfully!
echo.
echo Next steps:
echo 1. Update .env file with your database credentials
echo 2. Activate virtual environment: venv\Scripts\activate.bat
echo 3. Run the application: python main.py
echo ======================================================
pause
