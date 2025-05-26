#!/usr/bin/env python3
"""
Initialize Git repository for PDF Question Extraction and RAG System.
This script helps set up the repository for GitHub deployment.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def check_git_installed():
    """Check if Git is installed."""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """Initialize Git repository."""
    print("🚀 PDF Question Extraction and RAG System - Git Repository Setup")
    print("=" * 70)
    
    # Check if Git is installed
    if not check_git_installed():
        print("❌ Git is not installed. Please install Git first.")
        print("   Download from: https://git-scm.com/downloads")
        return False
    
    # Check if already a git repository
    if Path(".git").exists():
        print("ℹ️  Git repository already exists.")
        print("   Current status:")
        run_command("git status --porcelain", "Checking repository status")
        return True
    
    # Initialize git repository
    commands = [
        ("git init", "Initializing Git repository"),
        ("git add .", "Adding all files to staging"),
        ("git commit -m 'Initial commit: PDF Question Extraction and RAG System with secure environment variable management'", "Creating initial commit"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    print("\n🎉 Git repository initialized successfully!")
    print("\n📋 Next Steps:")
    print("1. Create a new repository on GitHub")
    print("2. Add the remote origin:")
    print("   git remote add origin https://github.com/yourusername/pdf-question-rag-system.git")
    print("3. Push to GitHub:")
    print("   git branch -M main")
    print("   git push -u origin main")
    print("4. Configure GitHub Secrets (see DEPLOYMENT.md)")
    print("5. Deploy to Streamlit Cloud")
    
    print("\n🔐 Security Reminder:")
    print("- ✅ API keys are stored in environment variables")
    print("- ✅ .env file is excluded from version control")
    print("- ✅ Only template files are committed")
    print("- ✅ GitHub Secrets will store production keys")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
