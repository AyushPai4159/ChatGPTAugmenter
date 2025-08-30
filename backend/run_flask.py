#!/usr/bin/env python3
"""
Python equivalent of run_flask.sh bash script.
Checks for virtual environment, validates files, and starts Flask server.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_header():
    """Print the application startup header."""
    print("🚀 Starting Semantic Search Flask Application")
    print("=============================================")


def check_virtual_environment():
    """
    Check if the virtual environment exists and is properly set up.
    
    Returns:
        Path or None: Path to venv if it exists, None otherwise
    """
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("❌ Error: Virtual environment not found!")
        print("📁 Expected location: backend/venv/")
        print("🔧 Please run the setup script to create the virtual environment:")
        print("   python setupBackend.py")
        print()
        print("💡 This will:")
        print("   - Create the virtual environment")
        print("   - Install all required dependencies")
        print("   - Set up the machine learning model")
        return None
    
    # Check if the virtual environment has a Python executable
    if platform.system() == "Windows":
        python_executable = venv_path / "Scripts" / "python.exe"
    else:
        python_executable = venv_path / "bin" / "python"
    
    if not python_executable.exists():
        print("❌ Error: Virtual environment is incomplete!")
        print(f"🐍 Python executable not found at: {python_executable}")
        print("🔧 Please run the setup script to recreate the virtual environment:")
        print("   python setupBackend.py")
        return None
    
    print(f"✅ Virtual environment found: {venv_path}")
    print(f"🐍 Python executable: {python_executable}")
    return venv_path


def get_venv_python(venv_path):
    """
    Get the Python executable path from the virtual environment.
    
    Args:
        venv_path (Path): Path to the virtual environment directory
        
    Returns:
        Path: Path to the Python executable
    """
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def validate_required_files():
    """
    Validate that all required files exist.
    
    Returns:
        bool: True if all files exist, False otherwise
    """
    required_files = [
        ("my_model_dir/config.json", "Model directory 'my_model_dir' not found or incomplete!")
    ]
    
    all_files_exist = True
    
    for file_path, error_message in required_files:
        if not Path(file_path).exists():
            print(f"❌ Error: {error_message}")
            print("Please ensure the required files are in the correct location.")
            all_files_exist = False
    
    if all_files_exist:
        print("✅ All required files found!")
    
    return all_files_exist
    


def start_flask_server(venv_path):
    """
    Start the Flask server using the virtual environment Python.
    
    Args:
        venv_path (Path): Path to the virtual environment directory
    """
    print()
    print("🌐 Starting Flask server...")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    python_executable = get_venv_python(venv_path)
    
    if not Path("app.py").exists():
        print("❌ Error: app.py not found!")
        sys.exit(1)
    
    try:
        # Run the Flask app
        subprocess.run([str(python_executable), "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Flask server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Flask server stopped by user")


def main():
    """
    Main function that checks venv, validates files, and starts Flask server.
    """
    print_header()
    
    # Check for virtual environment first
    venv_path = check_virtual_environment()
    if venv_path is None:
        sys.exit(1)
    
    # Validate required files
    if not validate_required_files():
        print()
        print("🔧 If files are missing, try running setup again:")
        print("   python setupBackend.py")
        sys.exit(1)
    
    # Start Flask server using the virtual environment
    start_flask_server(venv_path)


if __name__ == "__main__":
    main()
