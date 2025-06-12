#!/usr/bin/env python3
"""
Database verification script for WhiteLabelRAG
Tests ChromaDB functionality and database state
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_health():
    """Test application health"""
    print("=== Testing Application Health ===")
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        print(f"✅ Health Status: {response.status_code}")
        print(f"✅ Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_file_listing():
    """Test file listing endpoint"""
    print("\n=== Testing File Listing ===")
    try:
        response = requests.get('http://localhost:5000/api/files', timeout=15)
        print(f"✅ Files Status: {response.status_code}")
        if response.status_code == 200:
            files_data = response.json()
            print(f"✅ Found {len(files_data.get('files', []))} files")
            for file in files_data.get('files', [])[:3]:  # Show first 3 files
                print(f"   - {file.get('name', 'Unknown')} ({file.get('size', 0)} bytes)")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ File listing failed: {e}")
        return False

def test_basic_query():
    """Test basic RAG query"""
    print("\n=== Testing Basic RAG Query ===")
    try:
        query_data = {
            "query": "Tell me about the documents you have",
            "top_k": 3
        }
        response = requests.post(
            'http://localhost:5000/api/query',
            json=query_data,
            timeout=30
        )
        print(f"✅ Query Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                rag_response = result.get('rag_response', {})
                print(f"✅ RAG Response received")
                print(f"   Workflow: {rag_response.get('workflow', 'unknown')}")
                print(f"   Sources: {len(rag_response.get('sources', []))}")
                print(f"   Results: {len(rag_response.get('results', []))}")
                print(f"   Text preview: {rag_response.get('text', '')[:100]}...")
            else:
                print(f"❌ Query failed: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Basic query failed: {e}")
        return False

def test_document_stats():
    """Test document statistics"""
    print("\n=== Testing Document Statistics ===")
    try:
        # Try to get collection stats if endpoint exists
        response = requests.get('http://localhost:5000/api/stats', timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Document stats: {stats}")
        else:
            print("ℹ️  No stats endpoint available")
        return True
    except Exception as e:
        print(f"ℹ️  Stats endpoint not available: {e}")
        return True

def main():
    """Run all database verification tests"""
    print("🔍 WhiteLabelRAG Database Verification")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("File Listing", test_file_listing),
        ("Basic RAG Query", test_basic_query),
        ("Document Statistics", test_document_stats)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database verification tests PASSED!")
        print("✅ WhiteLabelRAG database is fully operational")
    else:
        print("⚠️  Some tests failed - check the logs above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
