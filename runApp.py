#!/usr/bin/env python3
"""
Backend Flask Runner
Runs the run_flask.py script from the backend directory.
This script provides a convenient way to start the Flask application from the root directory.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """
    Main function that runs the backend run_flask.py script.
    """
    print("🚀 ChatGPT Augmenter Flask Server")
    print("=================================")
    print("This will start the Flask backend server from the root directory.\n")
    
    # Get the current script's directory (root)
    root_dir = Path(__file__).parent
    
    # Path to the backend run_flask.py script
    backend_flask_path = root_dir / "backend" / "run_flask.py"
    
    # Check if the backend flask script exists
    if not backend_flask_path.exists():
        print("❌ Error: backend/run_flask.py not found!")
        print(f"Expected location: {backend_flask_path}")
        print("Please ensure the backend directory contains run_flask.py")
        sys.exit(1)
    
    print(f"📂 Running Flask server from: {backend_flask_path}")
    print("🔄 Starting Flask application...\n")
    print("📝 Note: Use Ctrl+C to stop the server")
    print("🌐 The server will be available at http://localhost:8080\n")
    
    try:
        # Run the backend run_flask.py script
        result = subprocess.run(
            [sys.executable, str(backend_flask_path)],
            cwd=backend_flask_path.parent,  # Run from backend directory
            check=True
        )
        
        print("\n✅ Flask server stopped gracefully")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Flask server failed with return code: {e.returncode}")
        print("Please check the error messages above and try again.")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Flask server stopped by user")
        print("✅ Server shutdown complete")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
