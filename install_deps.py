#!/usr/bin/env python3
"""
Simple dependency installer for Text Sentiment Extraction application.
Run this first if setup.py fails due to missing dependencies.
"""

import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")

    requirements_file = Path("config/requirements.txt")
    if not requirements_file.exists():
        print(f"[ERROR] Requirements file not found: {requirements_file}")
        return False

    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ])
        print("[OK] Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        return False

def main():
    """Main installation function."""
    print("Installing dependencies for Text Sentiment Extraction")
    print("=" * 50)

    if install_dependencies():
        print("\n[SUCCESS] Dependencies installed!")
        print("\nNext steps:")
        print("1. Run: python setup.py")
        print("2. Or manually configure your database and run: python main.py")
    else:
        print("\n[ERROR] Installation failed!")
        print("Please check the error messages above.")
        return False

    return True

if __name__ == "__main__":
    main()