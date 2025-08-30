#!/usr/bin/env python3
"""
Python equivalent of load.sh bash script.
Runs the data loading and processing pipeline in sequence.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_script(script_name, working_dir):
    """
    Run a Python script in the specified directory.
    
    Args:
        script_name (str): Name of the Python script to run
        working_dir (Path): Directory where the script is located
    
    Returns:
        bool: True if script ran successfully, False otherwise
    """
    try:
        print(f"Running {script_name}...")
        
        # Change to the working directory and run the script
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ {script_name} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {script_name}:")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    
    except FileNotFoundError:
        print(f"✗ Error: {script_name} not found in {working_dir}")
        return False


def main():
    """
    Main function that replicates the bash script functionality.
    Navigates to pythonFiles directory and runs the three scripts in sequence.
    """
    # Get the current script's directory (backend)
    current_dir = Path(__file__).parent
    
    # Navigate to pythonFiles directory (equivalent to cd .. && cd pythonFiles)
    python_files_dir = current_dir / "pythonFiles"
    
    if not python_files_dir.exists():
        print(f"✗ Error: pythonFiles directory not found at {python_files_dir}")
        sys.exit(1)
    
    print(f"Working directory: {python_files_dir}")
    print("Starting data loading and processing pipeline...\n")
    
    # Scripts to run in sequence (equivalent to the bash script)
    scripts = [
        "createVenv.py",
        "preload.py", 
    ]
    
    # Run each script in sequence
    for script in scripts:
        success = run_script(script, python_files_dir)
        if not success:
            print(f"\n✗ Pipeline failed at {script}")
            sys.exit(1)
        print()  # Add blank line between scripts
    
    print("✓ All scripts completed successfully!")
    print("Data loading and processing pipeline finished.")


if __name__ == "__main__":
    main()
