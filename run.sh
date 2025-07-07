#!/bin/bash

echo "==============================="
echo "PostgreSQL Data Import Suite"
echo "==============================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    python3 setup.py
    echo ""
    echo "Setup completed. Please update .env file with your database credentials."
    echo "Then run this script again."
    read -p "Press any key to continue..."
    exit 1
fi

# Activate virtual environment and run application
echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting application..."
python main.py

echo ""
echo "Application finished."
read -p "Press any key to continue..."
