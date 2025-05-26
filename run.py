"""
Simple script to run the Streamlit application with proper configuration.
"""
import subprocess
import sys
import os
from pathlib import Path

def check_setup():
    """Check if the setup is complete."""
    required_files = [
        "app.py",
        "config.py",
        "requirements.txt"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease run 'python setup.py' first.")
        return False
    
    return True

def run_streamlit():
    """Run the Streamlit application."""
    try:
        print("🚀 Starting PDF Question Extraction and RAG Answering System...")
        print("📱 The app will open in your default browser")
        print("🔗 URL: http://localhost:8501")
        print("\n" + "="*60)
        print("Press Ctrl+C to stop the application")
        print("="*60 + "\n")
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        print("\nTry running manually:")
        print("   streamlit run app.py")

def main():
    """Main function."""
    print("PDF Question Extraction and RAG Answering System")
    print("=" * 60)
    
    # Check setup
    if not check_setup():
        return
    
    # Run application
    run_streamlit()

if __name__ == "__main__":
    main()
