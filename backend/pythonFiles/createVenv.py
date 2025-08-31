#!/usr/bin/env python3
"""
Virtual Environment Creator
Creates a Python virtual environment, upgrades pip, and installs requirements.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def run_command(command, cwd=None, description="Running command"):
    """
    Run a subprocess command with error handling.
    
    Args:
        command (list): Command to run as list of strings
        cwd (str): Working directory for the command
        description (str): Description of what the command does
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description} failed")
        if e.stderr:
            print(f"Error details: {e.stderr.strip()}")
        if e.stdout:
            print(f"Output: {e.stdout.strip()}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during {description}: {e}")
        return False


def create_virtual_environment():
    """
    Create and set up a virtual environment with all dependencies.
    """
    print("🚀 Python Virtual Environment Setup")
    print("===================================")
    
    # Get the backend directory (parent of pythonFiles)
    backend_dir = Path(__file__).parent.parent
    venv_dir = backend_dir / "venv"
    requirements_file = backend_dir / "requirements.txt"
    
    print(f"📂 Backend directory: {backend_dir}")
    print(f"🐍 Virtual environment: {venv_dir}")
    print(f"📋 Requirements file: {requirements_file}")
    
    # Check if requirements.txt exists
    if not requirements_file.exists():
        print("❌ Error: requirements.txt not found!")
        print(f"Expected location: {requirements_file}")
        return False
    
    # Step 1: Create virtual environment
    print("\n📦 Step 1: Creating virtual environment...")
    try:
        if venv_dir.exists():
            print(f"⚠️  Virtual environment already exists at {venv_dir}")
            print("🔄 Skipping creation...")
        else:
            venv.create(venv_dir, with_pip=True)
            print(f"✅ Virtual environment created at {venv_dir}")
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False
    
    # Determine the correct python executable path in venv
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"
    
    # Verify python executable exists
    if not venv_python.exists():
        print(f"❌ Error: Python executable not found at {venv_python}")
        return False
    
    print(f"🐍 Using Python: {venv_python}")
    
    # Step 2: Upgrade pip
    print("\n⬆️  Step 2: Upgrading pip...")
    if not run_command(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=backend_dir,
        description="Upgrading pip"
    ):
        print("⚠️  Pip upgrade failed, but continuing with installation...")
    else:
        print("✅ Pip upgraded successfully")
    
    # Step 3: Install requirements
    print("\n📦 Step 3: Installing requirements...")
    if not run_command(
        [str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)],
        cwd=backend_dir,
        description="Installing requirements"
    ):
        print("❌ Failed to install requirements")
        return False
    
    print("✅ Requirements installed successfully")
    
    # Step 4: Verify installation
    print("\n🔍 Step 4: Verifying installation...")
    if not run_command(
        [str(venv_python), "-m", "pip", "list"],
        cwd=backend_dir,
        description="Listing installed packages"
    ):
        print("⚠️  Could not verify installation, but setup may be complete")
    
    # Success message
    print("\n🎉 Virtual environment setup complete!")
    print("=" * 45)
    print("📝 Next steps:")
    print(f"   1. Activate the environment:")
    if sys.platform == "win32":
        print(f"      {venv_dir / 'Scripts' / 'activate.bat'}")
    else:
        print(f"      source {venv_dir / 'bin' / 'activate'}")
    print("   2. Run your Python scripts")
    print("   3. Deactivate when done: deactivate")
    
    return True


def main():
    """
    Main function to create virtual environment.
    """
    try:
        success = create_virtual_environment()
        if success:
            print("\n✅ Virtual environment setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Virtual environment setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()