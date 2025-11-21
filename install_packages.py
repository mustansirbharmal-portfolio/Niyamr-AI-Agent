#!/usr/bin/env python3
"""
Alternative package installer for Windows with Python 3.13
This script installs packages one by one to handle dependency issues better
"""

import subprocess
import sys
import time

def install_package(package):
    """Install a single package with retry logic"""
    print(f"📦 Installing {package}...")
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "--user"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"  ✅ {package} installed successfully")
                return True
            else:
                print(f"  ❌ Attempt {attempt + 1} failed for {package}")
                if attempt < max_retries - 1:
                    print(f"  🔄 Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(f"  ❌ Failed to install {package} after {max_retries} attempts")
                    print(f"  Error: {result.stderr}")
                    return False
                    
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Timeout installing {package} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                print(f"  🔄 Retrying...")
            else:
                return False
        except Exception as e:
            print(f"  ❌ Error installing {package}: {e}")
            return False
    
    return False

def main():
    """Main installation function"""
    print("🚀 Installing Niyamr AI Dependencies")
    print("=" * 50)
    
    # First, upgrade pip
    print("📦 Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user"])
    
    # Core packages first (in order of dependency)
    core_packages = [
        "numpy>=1.26.0",
        "pandas>=2.0.0", 
        "requests>=2.31.0",
        "python-dotenv>=1.0.0"
    ]
    
    # Azure packages
    azure_packages = [
        "azure-core",
        "azure-storage-blob>=12.19.0",
        "azure-cosmos>=4.5.0", 
        "azure-search-documents>=11.4.0"
    ]
    
    # AI/ML packages
    ai_packages = [
        "openai>=1.3.0",
        "tiktoken>=0.5.0",
        "langchain>=0.0.300",
        "langchain-openai>=0.0.2"
    ]
    
    # Web framework packages
    web_packages = [
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "streamlit>=1.28.0"
    ]
    
    # PDF processing packages
    pdf_packages = [
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.9.0"
    ]
    
    all_package_groups = [
        ("Core packages", core_packages),
        ("Azure packages", azure_packages), 
        ("AI/ML packages", ai_packages),
        ("Web framework packages", web_packages),
        ("PDF processing packages", pdf_packages)
    ]
    
    failed_packages = []
    
    for group_name, packages in all_package_groups:
        print(f"\n📋 Installing {group_name}...")
        for package in packages:
            if not install_package(package):
                failed_packages.append(package)
    
    print("\n" + "=" * 50)
    if not failed_packages:
        print("🎉 All packages installed successfully!")
        print("\n✅ You can now run: python run_app.py")
        return True
    else:
        print(f"❌ Failed to install {len(failed_packages)} packages:")
        for package in failed_packages:
            print(f"  - {package}")
        
        print("\n🔧 Try installing failed packages manually:")
        for package in failed_packages:
            print(f"  pip install {package}")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
