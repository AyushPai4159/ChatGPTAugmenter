#!/usr/bin/env python3
"""
Frontend React Runner
Runs npm start in the react-app directory.
This script provides a convenient way to start the React development server from the root directory.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """
    Main function that runs npm start in the react-app directory.
    """
    print("🚀 ChatGPT Augmenter React Server")
    print("=================================")
    print("This will start the React development server from the root directory.\n")
    
    # Get the current script's directory (root)
    root_dir = Path(__file__).parent
    
    # Path to the react-app directory
    react_app_path = root_dir / "react-app"
    
    # Check if the react-app directory exists
    if not react_app_path.exists():
        print("❌ Error: react-app directory not found!")
        print(f"Expected location: {react_app_path}")
        print("Please ensure the react-app directory exists")
        sys.exit(1)
    
    # Check if package.json exists
    package_json_path = react_app_path / "package.json"
    if not package_json_path.exists():
        print("❌ Error: package.json not found in react-app directory!")
        print(f"Expected location: {package_json_path}")
        print("Please run setupFrontend.py first to install dependencies")
        sys.exit(1)
    
    # Check if node_modules exists (basic check for installed dependencies)
    node_modules_path = react_app_path / "node_modules"
    if not node_modules_path.exists():
        print("❌ Error: node_modules directory not found!")
        print("Please run setupFrontend.py first to install dependencies:")
        print("   python setupFrontend.py")
        sys.exit(1)
    
    print(f"📂 Starting React server from: {react_app_path}")
    print("🔄 Running npm start...\n")
    print("📝 Note: Use Ctrl+C to stop the server")
    print("🌐 The React app will be available at http://localhost:3000")
    print("🔗 It should automatically open in your default browser\n")
    
    try:
        # Check if npm is available
        npm_check = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        
        if npm_check.returncode != 0:
            print("❌ Error: npm is not installed or not available in PATH")
            print("Please install Node.js and npm first")
            print("Visit: https://nodejs.org/")
            sys.exit(1)
        
        print(f"📦 Using npm version: {npm_check.stdout.strip()}")
        print("🎯 Starting development server...\n")
        
        # Run npm start in the react-app directory
        result = subprocess.run(
            ["npm", "start"],
            cwd=react_app_path,
            check=True
        )
        
        print("\n✅ React development server stopped gracefully")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ React server failed with return code: {e.returncode}")
        print("Please check the error messages above and try again.")
        print("Common solutions:")
        print("  - Run setupFrontend.py to install/update dependencies")
        print("  - Check if port 3000 is already in use")
        print("  - Clear npm cache: npm cache clean --force")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️ React development server stopped by user")
        print("✅ Server shutdown complete")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
