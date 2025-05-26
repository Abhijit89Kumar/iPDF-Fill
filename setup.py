"""
Setup script for the PDF Question Extraction and RAG system.
"""
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "temp",
        "outputs",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_files():
    """Check if required files exist."""
    required_files = [
        "files/IndianMovie_KnowledgeBase.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("Please ensure these files are available or upload them through the app.")
    else:
        print("✅ All required files found!")

def main():
    """Main setup function."""
    print("🚀 Setting up PDF Question Extraction and RAG system...")
    print("=" * 60)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create directories
    create_directories()
    
    # Check files
    check_files()
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("\nTo run the application:")
    print("  streamlit run app.py")
    print("\nTo run with custom port:")
    print("  streamlit run app.py --server.port 8501")

if __name__ == "__main__":
    main()
