#!/usr/bin/env python3
"""
Setup script for Niyamr AI Legislative Document Analyzer
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    # First try the simple requirements
    try:
        print("🔄 Trying simple installation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_simple.txt", "--user"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Simple installation failed, trying alternative method...")
        
        # Try the alternative installer
        try:
            result = subprocess.run([sys.executable, "install_packages.py"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Alternative installation successful!")
                return True
            else:
                print(f"❌ Alternative installation failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error with alternative installer: {e}")
        
        # Final fallback - manual instructions
        print("\n🔧 Manual installation required:")
        print("Please run the following commands one by one:")
        print("  pip install --upgrade pip")
        print("  pip install numpy pandas requests python-dotenv")
        print("  pip install azure-storage-blob azure-cosmos azure-search-documents")
        print("  pip install openai tiktoken langchain langchain-openai")
        print("  pip install flask flask-cors streamlit")
        print("  pip install PyPDF2 pdfplumber")
        
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    required_vars = [
        "COSMOS_ENDPOINT",
        "COSMOS_KEY", 
        "AZURE_STORAGE_CONNECTION_STRING",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_ADMIN_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY"
    ]
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment file configured correctly!")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Niyamr AI Legislative Document Analyzer")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check environment file
    if not check_env_file():
        print("\n📝 Please ensure your .env file contains all required Azure credentials")
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Ensure your PDF is uploaded to Azure Blob Storage")
    print("2. Verify Azure Search index 'niyamr-ai-index' exists")
    print("3. Run the application with: python run_app.py")
    print("\n🌐 The application will be available at:")
    print("   - Streamlit UI: http://localhost:8501")
    print("   - Flask API: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
