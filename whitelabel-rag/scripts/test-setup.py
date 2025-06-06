#!/usr/bin/env python3
"""
Test setup script to verify WhiteLabelRAG installation
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.9+")
        return False

def check_virtual_environment():
    """Check if virtual environment exists and is activated."""
    print("\n📦 Checking virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment directory found")
        
        # Check if we're in the virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment is activated")
            return True
        else:
            print("⚠️ Virtual environment exists but not activated")
            print("💡 Activate with: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)")
            return False
    else:
        print("❌ Virtual environment not found")
        print("💡 Create with: python -m venv venv")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📚 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask-cors',
        'flask-socketio',
        'chromadb',
        'google-generativeai',
        'python-dotenv',
        'PyPDF2',
        'python-docx',
        'markdown',
        'beautifulsoup4',
        'sentence-transformers',
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                import dotenv
            elif package == 'python-docx':
                import docx
            elif package == 'beautifulsoup4':
                import bs4
            elif package == 'google-generativeai':
                import google.generativeai
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages are installed")
        return True

def check_directories():
    """Check if required directories exist."""
    print("\n📁 Checking directories...")
    
    required_dirs = ['uploads', 'chromadb_data', 'logs']
    all_exist = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ (will be created automatically)")
            all_exist = False
    
    return all_exist

def check_environment_variables():
    """Check environment variables."""
    print("\n🔧 Checking environment variables...")
    
    # Load .env file if it exists
    if Path('.env').exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file found and loaded")
    else:
        print("���️ .env file not found")
    
    # Check GEMINI_API_KEY
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(api_key)} characters)")
        return True
    else:
        print("❌ GEMINI_API_KEY is not set")
        print("💡 Set with: export GEMINI_API_KEY=your_key (Linux/Mac) or set GEMINI_API_KEY=your_key (Windows)")
        print("💡 Or add to .env file: GEMINI_API_KEY=your_key")
        print("💡 Get API key from: https://makersuite.google.com/app/apikey")
        return False

def test_imports():
    """Test importing main application modules."""
    print("\n🧪 Testing application imports...")
    
    try:
        # Test basic imports
        sys.path.insert(0, 'app')
        
        from app.config import Config
        print("✅ Config module")
        
        from app.services.base_assistant import BaseAssistant
        print("✅ BaseAssistant module")
        
        # Test if we can create the app (without starting it)
        os.environ.setdefault('GEMINI_API_KEY', 'test-key-for-import-test')
        from app import create_app
        print("✅ App creation module")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def run_basic_functionality_test():
    """Run basic functionality tests."""
    print("\n🔬 Running basic functionality tests...")
    
    try:
        # Test document processor
        from app.services.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        print("✅ DocumentProcessor initialization")
        
        # Test supported formats
        formats = processor.get_supported_formats()
        if len(formats) >= 4:  # Should support at least PDF, DOCX, TXT, MD
            print(f"✅ Document formats supported: {', '.join(formats)}")
        else:
            print(f"⚠️ Limited document format support: {', '.join(formats)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def main():
    """Run all setup tests."""
    print("🚀 WhiteLabelRAG Setup Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Environment Variables", check_environment_variables),
        ("Application Imports", test_imports),
        ("Basic Functionality", run_basic_functionality_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! WhiteLabelRAG is ready to run.")
        print("🚀 Start the application with: python run.py")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix the issues above.")
        print("💡 Run the setup script: scripts/setup.sh or scripts/setup.bat")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)