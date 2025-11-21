import subprocess
import sys
import time
import threading
import webbrowser
from pathlib import Path

def run_flask():
    """Run Flask backend"""
    print("Starting Flask backend...")
    subprocess.run([sys.executable, "app.py"])

def run_streamlit():
    """Run Streamlit frontend"""
    print("Starting Streamlit frontend...")
    time.sleep(3)  # Wait for Flask to start
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"])

def main():
    """Main function to run both Flask and Streamlit"""
    print("🚀 Starting Niyamr AI Legislative Document Analyzer")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [".env", "app.py", "streamlit_app.py", "config.py", "azure_services.py", "document_processor.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: Required file '{file}' not found!")
            return
    
    print("✅ All required files found")
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("⏳ Waiting for Flask backend to start...")
    time.sleep(5)
    
    # Start Streamlit
    print("🌐 Starting Streamlit frontend...")
    print("📱 Streamlit will be available at: http://localhost:8501")
    print("🔧 Flask API will be available at: http://localhost:5000")
    print("\n🎯 Navigate to http://localhost:8501 in your browser")
    
    # Open browser automatically
    time.sleep(2)
    webbrowser.open("http://localhost:8501")
    
    # Run Streamlit
    run_streamlit()

if __name__ == "__main__":
    main()
