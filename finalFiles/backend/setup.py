#!/usr/bin/env python3
"""
Python equivalent of setup.sh bash script.
Runs the complete setup pipeline: cleanup followed by data loading and processing.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_python_script(script_name, script_path):
    """
    Run a Python script and handle its output.
    
    Args:
        script_name (str): Name of the script for display purposes
        script_path (Path): Full path to the Python script
    
    Returns:
        bool: True if script ran successfully, False otherwise
    """
    try:
        print(f"🔄 Running {script_name}...")
        
        # Run the Python script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            check=True,
            text=True
        )
        
        print(f"✅ {script_name} completed successfully\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}:")
        print(f"Return code: {e.returncode}")
        return False
    
    except FileNotFoundError:
        print(f"❌ Error: {script_name} not found at {script_path}")
        return False


def main():
    """
    Main function that replicates the bash script functionality.
    Runs delete.py followed by load.py to complete the setup pipeline.
    """
    print("🚀 Starting ChatGPT Augmenter Setup Pipeline")
    print("============================================")
    print("This will clean up existing data and reload everything fresh.\n")
    
    # Get the current script's directory (backend)
    current_dir = Path(__file__).parent
    
    # Define the scripts to run in sequence
    scripts = [
        ("Cleanup (delete.py)",  "delete.py"),
        ("Data Loading (load.py)", "load.py")
    ]
    
    # Run each script in sequence
    for script_name, script_path in scripts:
        success = run_python_script(script_name, script_path)
        if not success:
            print(f"\n❌ Setup pipeline failed at {script_name}")
            print("Please check the error messages above and try again.")
            sys.exit(1)
    
    print("🎉 Setup pipeline completed successfully!")
    print("✅ All data has been cleaned and reloaded")
    print("🚀 You can now run the Flask application with run_flask.py")


if __name__ == "__main__":
    # Add confirmation prompt since this involves deletion
    print("⚠️  SETUP PIPELINE WARNING ⚠️")
    print("This will:")
    print("1. DELETE existing model and data files")
    print("2. RELOAD and reprocess all data from scratch")
    print()
    print("Files that will be deleted:")
    print("- my_model_dir/ (entire directory)")
    print("- venv/ (entire directory)")
    print("- data/conversations") 
    print()
    print("Then the following will be regenerated:")
    print("- Download ML model (preload.py)")
    print("Create virtual environment (createVenv.py)")
    print()
    
    response = input("Are you sure you want to continue? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        main()
    else:
        print("Setup cancelled.")
        sys.exit(0)
