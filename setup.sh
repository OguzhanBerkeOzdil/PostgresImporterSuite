#!/bin/bash

# PostgreSQL Data Import Suite - Setup Script (Unix/Linux/macOS)

echo "======================================================"
echo "    PostgreSQL Data Import Suite - Setup"
echo "======================================================"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo "✓ Virtual environment created successfully"
else
    echo "✗ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment and install requirements
echo "Installing required packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Requirements installed successfully"
else
    echo "✗ Failed to install requirements"
    exit 1
fi

# Setup environment file
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Setting up environment configuration..."
    cp .env.example .env
    echo "✓ Environment file created from template"
    echo "⚠  Please update .env file with your database credentials"
elif [ -f ".env" ]; then
    echo "✓ Environment file already exists"
else
    echo "✗ No environment template found"
fi

echo ""
echo "======================================================"
echo "✓ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your database credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python main.py"
echo "======================================================"
