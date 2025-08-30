#!/usr/bin/env python3
"""
Backend Setup Runner
Runs the setup.py script from the backend directory.
This script provides a convenient way to run the backend setup from the root directory.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """
    Main function that runs the backend setup.py script.
    """
    print("🚀 ChatGPT Augmenter Backend Setup")
    print("==================================")
    print("This will run the backend setup pipeline from the root directory.\n")
    
    # Get the current script's directory (root)
    root_dir = Path(__file__).parent
    
    # Path to the backend setup.py script
    backend_setup_path = root_dir / "backend" / "setup.py"
    
    # Check if the backend setup script exists
    if not backend_setup_path.exists():
        print("❌ Error: backend/setup.py not found!")
        print(f"Expected location: {backend_setup_path}")
        print("Please ensure the backend directory contains setup.py")
        sys.exit(1)
    
    print(f"📂 Running setup from: {backend_setup_path}")
    print("🔄 Executing backend setup...\n")
    
    try:
        # Run the backend setup.py script
        result = subprocess.run(
            [sys.executable, str(backend_setup_path)],
            cwd=backend_setup_path.parent,  # Run from backend directory
            check=True
        )
        
        print("\n✅ Backend setup completed successfully!")
        print("🚀 You can now run the Flask application from the backend directory")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Backend setup failed with return code: {e.returncode}")
        print("Please check the error messages above and try again.")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
