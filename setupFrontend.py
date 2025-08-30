#!/usr/bin/env python3
"""
Frontend Setup Runner
Runs npm install in the react-app directory.
This script provides a convenient way to set up the React frontend from the root directory.
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """
    Main function that runs npm install in the react-app directory.
    """
    print("🚀 ChatGPT Augmenter Frontend Setup")
    print("====================================")
    print("This will install React dependencies from the root directory.\n")
    
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
        print("Please ensure the react-app directory contains a valid package.json")
        sys.exit(1)
    
    installNode = True
    # Check if node_modules already exists
    node_modules_path = react_app_path / "node_modules"
    if node_modules_path.exists():
        installNode = False
        print("📦 node_modules directory already exists!")
        print(f"📁 Location: {node_modules_path}")
        print("🔍 Checking if dependencies are up to date...")
        
        # Check if package-lock.json exists (indicates previous npm install)
        package_lock_path = react_app_path / "package-lock.json"
        if package_lock_path.exists():
            print("✅ Dependencies appear to be installed (package-lock.json found)")
            print("🔄 Running npm install to ensure dependencies are current...")
        else:
            print("⚠️  No package-lock.json found, running npm install to ensure proper setup...")
    else:
        print("📦 node_modules not found, will install fresh dependencies")
    
    print(f"📂 Installing dependencies in: {react_app_path}")
    print("🔄 Running npm install...\n")
    
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
        
        # Run npm install in the react-app directory
        if(installNode):
            result = subprocess.run(
            ["npm", "install"],
            cwd=react_app_path,
            check=True
        )
        
        print("\n✅ Frontend setup completed successfully!")
        print("🚀 You can now run the React application with:")
        print("   cd react-app && npm start")
        print("   or use runFrontend.py from the root directory")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ npm install failed with return code: {e.returncode}")
        print("Please check the error messages above and try again.")
        print("Common solutions:")
        print("  - Clear npm cache: npm cache clean --force")
        print("  - Delete node_modules and try again")
        print("  - Check your internet connection")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
