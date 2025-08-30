#!/usr/bin/env python3
"""
Python equivalent of delete.sh bash script.
Safely removes generated files and directories from the data processing pipeline.
"""

import os
import sys
import shutil
from pathlib import Path


def safe_remove_file(file_path):
    """
    Safely remove a file if it exists.
    
    Args:
        file_path (Path): Path to the file to remove
    
    Returns:
        bool: True if file was removed or didn't exist, False if error occurred
    """
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"✓ Removed file: {file_path}")
            return True
        else:
            print(f"• File not found (skipping): {file_path}")
            return True
    except Exception as e:
        print(f"✗ Error removing file {file_path}: {e}")
        return False


def safe_remove_directory(dir_path):
    """
    Safely remove a directory and its contents if it exists.
    
    Args:
        dir_path (Path): Path to the directory to remove
    
    Returns:
        bool: True if directory was removed or didn't exist, False if error occurred
    """
    try:
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            print(f"✓ Removed directory: {dir_path}")
            return True
        elif dir_path.exists():
            print(f"✗ Path exists but is not a directory: {dir_path}")
            return False
        else:
            print(f"• Directory not found (skipping): {dir_path}")
            return True
    except Exception as e:
        print(f"✗ Error removing directory {dir_path}: {e}")
        return False


def main():
    """
    Main function that replicates the bash script functionality.
    Removes the model directory and generated data files.
    """
    # Get the current script's directory (backend)
    current_dir = Path(__file__).parent
    
    print("Starting cleanup of generated files and directories...")
    print(f"Working from: {current_dir}\n")
    
    # Define paths to remove (equivalent to the bash script)
    items_to_remove = [
        # Remove model directory (equivalent to rm -R ../my_model_dir)
        ("directory", current_dir / "../my_model_dir"),
        # Remove output files (equivalent to rm ../data/output.json and rm ../data/doc_embeddings.npy)
        ("file", current_dir / "../data/output.json"),
        ("file", current_dir / "../data/doc_embeddings.npy")
    ]
    
    success_count = 0
    total_count = len(items_to_remove)
    
    # Process each item
    for item_type, path in items_to_remove:
        # Resolve the path to handle the .. navigation
        resolved_path = path.resolve()
        
        if item_type == "directory":
            success = safe_remove_directory(resolved_path)
        else:  # file
            success = safe_remove_file(resolved_path)
        
        if success:
            success_count += 1
    
    print(f"\nCleanup completed: {success_count}/{total_count} operations successful")
    
    if success_count == total_count:
        print("✓ All cleanup operations completed successfully!")
    else:
        print("⚠ Some cleanup operations failed. Check the messages above.")
        sys.exit(1)


if __name__ == "__main__":
    # Add confirmation prompt for safety
    print("This will delete the following items:")
    print("- ../my_model_dir/ (entire directory)")
    print("- ../data/output.json")
    print("- ../data/doc_embeddings.npy")
    print()
    
    response = input("Are you sure you want to continue? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        main()
    else:
        print("Cleanup cancelled.")
        sys.exit(0)
