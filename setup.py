#!/usr/bin/env python3
"""
Setup script for PostgreSQL Data Import Suite
"""

import os
import sys
import subprocess
from pathlib import Path

def create_virtual_environment():
    """Create and activate virtual environment."""
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        # Determine pip path based on OS
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip.exe")
        else:  # Unix/Linux/MacOS
            pip_path = Path("venv/bin/pip")
        
        if not pip_path.exists():
            print("✗ Could not find pip in virtual environment")
            return False
        
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def setup_environment_file():
    """Setup environment configuration file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Setting up environment configuration...")
        try:
            with open(env_example, 'r') as source:
                content = source.read()
            
            with open(env_file, 'w') as target:
                target.write(content)
            
            print("✓ Environment file created from template")
            print("⚠  Please update .env file with your database credentials")
            return True
        except Exception as e:
            print(f"✗ Failed to create environment file: {e}")
            return False
    elif env_file.exists():
        print("✓ Environment file already exists")
        return True
    else:
        print("✗ No environment template found")
        return False

def main():
    """Main setup function."""
    print("="*60)
    print("    PostgreSQL Data Import Suite - Setup")
    print("="*60)
    
    success = True
    
    # Create virtual environment
    success &= create_virtual_environment()
    
    # Install requirements
    success &= install_requirements()
    
    # Setup environment file
    success &= setup_environment_file()
    
    print("\n" + "="*60)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your database credentials")
        print("2. Activate virtual environment:")
        if os.name == 'nt':  # Windows
            print("   .\\venv\\Scripts\\activate")
        else:  # Unix/Linux/MacOS
            print("   source venv/bin/activate")
        print("3. Run the application: python main.py")
    else:
        print("✗ Setup failed. Please check the errors above.")
    print("="*60)

if __name__ == "__main__":
    main()
