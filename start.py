#!/usr/bin/env python3
"""
Startup script for Logistics Management System
Checks dependencies and starts the application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ['flask', 'flask_sqlalchemy', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All Python dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Python dependencies")
            return False
    
    return True

def check_sqlite():
    """Check if SQLite is available"""
    try:
        import sqlite3
        print("✅ SQLite is available")
        return True
    except ImportError:
        print("❌ SQLite is not available")
        return False

def check_cpp_engine():
    """Check if C++ routing engine is compiled (optional)"""
    engine_path = Path("routing_engine")
    if engine_path.exists():
        print("✅ C++ routing engine found")
        return True
    else:
        print("⚠️  C++ routing engine not found (optional)")
        print("   Routing features will be limited")
        print("   To enable full routing: install g++ and jsoncpp, then run 'make all'")
        return False

def create_sample_map_data():
    """Create sample map data if it doesn't exist"""
    sample_file = Path("map_data.json")
    if not sample_file.exists():
        print("📁 Creating sample map data...")
        try:
            import shutil
            shutil.copy("sample_map_data.json", "map_data.json")
            print("✅ Sample map data created")
        except FileNotFoundError:
            print("⚠️  Sample map data not found, will use default network")

def main():
    """Main startup function"""
    print("\U0001F69A Logistics Management System - Startup Check")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n\U0001F4E6 Checking Python dependencies...")
    if not check_python_dependencies():
        sys.exit(1)
    
    print("\n\U0001F5C8\uFE0F  Checking SQLite...")
    if not check_sqlite():
        sys.exit(1)
    
    print("\n\u26A1 Checking C++ routing engine (optional)...")
    check_cpp_engine()  # Don't exit if this fails, it's optional
    
    print("\n\U0001F4C1 Setting up files...")
    create_sample_map_data()

    # Ensure users.csv exists
    users_csv = 'users.csv'
    if not os.path.exists(users_csv):
        import csv
        with open(users_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'username', 'password'])
    
    print("\n\U0001F389 All checks completed!")
    print("\nStarting the application...")
    print("\U0001F310 Open your browser and go to: http://localhost:5000")
    print("\U0001F4CA Click 'Initialize Database' to get started")
    print("\nPress Ctrl+C to stop the application")
    
    # Start the Flask application
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\U0001F44B Application stopped")
    except Exception as e:
        print(f"\u274C Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 