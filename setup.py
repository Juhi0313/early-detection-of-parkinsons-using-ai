"""
Setup script to initialize the project.
"""

import os
import subprocess
import sys

def main():
    print("=" * 60)
    print("Parkinson's Detection App - Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    print("\n1. Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("✗ Error installing dependencies. Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n2. Training model...")
    try:
        subprocess.check_call([sys.executable, "train_model.py"])
        print("✓ Model trained successfully!")
    except subprocess.CalledProcessError:
        print("✗ Error training model. Please run: python train_model.py")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Setup complete! You can now run the app with: python app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

