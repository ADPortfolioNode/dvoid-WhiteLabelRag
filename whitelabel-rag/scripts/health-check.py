#!/usr/bin/env python3
"""
Health check script for WhiteLabelRAG
"""

import os
import sys
import requests
import time
import json
from pathlib import Path

def check_server_health(url="http://localhost:5000", timeout=30):
    """Check if the server is running and healthy."""
    print(f"🏥 Checking server health at {url}...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is healthy!")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Service: {data.get('service', 'unknown')}")
                return True
        except requests.exceptions.ConnectionError:
            print("⏳ Waiting for server to start...")
            time.sleep(2)
        except requests.exceptions.Timeout:
            print("⏳ Server timeout, retrying...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Health check error: {e}")
            time.sleep(2)
    
    print(f"❌ Server health check failed after {timeout} seconds")
    return False

def test_api_endpoints(base_url="http://localhost:5000"):
    """Test basic API endpoints."""
    print(f"\n🧪 Testing API endpoints at {base_url}...")
    
    endpoints = [
        ("/health", "GET", None),
        ("/api/files", "GET", None),
        ("/api/decompose", "POST", {"message": "Hello, test message"}),
    ]
    
    results = []
    
    for endpoint, method, data in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"✅ {method} {endpoint} - {response.status_code}")
                results.append(True)
            else:
                print(f"⚠️ {method} {endpoint} - {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 API Test Results: {sum(results)}/{len(results)} passed ({success_rate:.1f}%)")
    
    return success_rate >= 80  # 80% success rate threshold

def check_websocket_connection(url="http://localhost:5000"):
    """Test WebSocket connection."""
    print(f"\n🔌 Testing WebSocket connection at {url}...")
    
    try:
        import socketio
        
        sio = socketio.Client()
        connected = False
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
            print("✅ WebSocket connected successfully")
        
        @sio.event
        def disconnect():
            print("🔌 WebSocket disconnected")
        
        sio.connect(url, wait_timeout=10)
        
        if connected:
            sio.disconnect()
            return True
        else:
            print("❌ WebSocket connection failed")
            return False
            
    except ImportError:
        print("⚠️ python-socketio not installed, skipping WebSocket test")
        return True  # Don't fail if socketio not available
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
        return False

def check_file_upload(base_url="http://localhost:5000"):
    """Test file upload functionality."""
    print(f"\n��� Testing file upload at {base_url}...")
    
    try:
        # Create a simple test file
        test_content = "This is a test document for WhiteLabelRAG health check."
        test_file_path = Path("test_upload.txt")
        
        with open(test_file_path, "w") as f:
            f.write(test_content)
        
        # Upload the file
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_upload.txt", f, "text/plain")}
            response = requests.post(f"{base_url}/api/files", files=files, timeout=30)
        
        # Clean up test file
        test_file_path.unlink()
        
        if response.status_code == 200:
            print("✅ File upload successful")
            return True
        else:
            print(f"❌ File upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File upload test error: {e}")
        # Clean up test file if it exists
        if test_file_path.exists():
            test_file_path.unlink()
        return False

def check_document_processing(base_url="http://localhost:5000"):
    """Test document processing functionality."""
    print(f"\n⚙️ Testing document processing at {base_url}...")
    
    try:
        # Create a test document
        test_content = """# Test Document
        
This is a test document for WhiteLabelRAG health check.

## Section 1
This document contains sample content to test the document processing pipeline.

## Section 2
The system should be able to extract text, create chunks, and store embeddings.
"""
        test_file_path = Path("test_document.md")
        
        with open(test_file_path, "w") as f:
            f.write(test_content)
        
        # Upload and process the document
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.md", f, "text/markdown")}
            response = requests.post(
                f"{base_url}/api/documents/upload_and_ingest_document", 
                files=files, 
                timeout=60
            )
        
        # Clean up test file
        test_file_path.unlink()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document processing successful")
            if "chunks_created" in data:
                print(f"   Chunks created: {data['chunks_created']}")
            return True
        else:
            print(f"❌ Document processing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Document processing test error: {e}")
        # Clean up test file if it exists
        if test_file_path.exists():
            test_file_path.unlink()
        return False

def main():
    """Run comprehensive health check."""
    print("🏥 WhiteLabelRAG Health Check")
    print("=" * 40)
    
    # Check if server is running
    if not check_server_health():
        print("\n❌ Server is not running or not healthy")
        print("💡 Start the server with: python run.py")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("API Endpoints", lambda: test_api_endpoints()),
        ("WebSocket Connection", lambda: check_websocket_connection()),
        ("File Upload", lambda: check_file_upload()),
        ("Document Processing", lambda: check_document_processing()),
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
    print("\n" + "=" * 40)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ HEALTHY" if result else "❌ UNHEALTHY"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall Health: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All health checks passed! WhiteLabelRAG is running properly.")
        return True
    else:
        print(f"\n⚠️ {total - passed} health check(s) failed.")
        print("💡 Check the server logs for more details")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)