#!/usr/bin/env python3
"""
Demo script for WhiteLabelRAG
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

class WhiteLabelRAGDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session_id = None
    
    def check_server(self):
        """Check if server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_message(self, message):
        """Send a message to the API."""
        try:
            data = {"message": message}
            if self.session_id:
                data["session_id"] = self.session_id
            
            response = requests.post(
                f"{self.base_url}/api/decompose",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if not self.session_id:
                    self.session_id = result.get("session_id")
                return result.get("response", {})
            else:
                return {"text": f"Error: {response.status_code}", "error": True}
                
        except Exception as e:
            return {"text": f"Error: {str(e)}", "error": True}
    
    def upload_document(self, file_path):
        """Upload a document."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f)}
                response = requests.post(
                    f"{self.base_url}/api/documents/upload_and_ingest_document",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Upload failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Upload error: {str(e)}"}
    
    def create_sample_document(self):
        """Create a sample document for demo."""
        content = """# WhiteLabelRAG Demo Document

## Introduction
This is a sample document created for the WhiteLabelRAG demonstration.

## Features
WhiteLabelRAG includes the following key features:

### Document Processing
- PDF file support
- Word document processing
- Text file handling
- Markdown parsing
- CSV data processing

### AI Capabilities
- Natural language conversations
- Document search and retrieval
- Question answering
- Task decomposition
- Function execution

### Technical Architecture
- Flask backend with REST API
- ChromaDB vector database
- Google Gemini AI integration
- Real-time WebSocket communication
- Responsive web interface

## Sample Data
Here are some sample facts for testing:

- The capital of France is Paris
- Python was created by Guido van Rossum
- The speed of light is approximately 299,792,458 meters per second
- Shakespeare wrote Romeo and Juliet
- The Great Wall of China is over 13,000 miles long

## Conclusion
This document demonstrates the document processing and retrieval capabilities of WhiteLabelRAG.
"""
        
        file_path = Path("demo_document.md")
        with open(file_path, "w") as f:
            f.write(content)
        
        return file_path
    
    def run_demo(self):
        """Run the complete demo."""
        print("🎬 WhiteLabelRAG Demo")
        print("=" * 50)
        
        # Check server
        print("1. Checking server status...")
        if not self.check_server():
            print("❌ Server is not running!")
            print("💡 Start with: python run.py")
            return False
        print("✅ Server is running")
        
        # Create and upload sample document
        print("\n2. Creating and uploading sample document...")
        doc_path = self.create_sample_document()
        
        upload_result = self.upload_document(doc_path)
        if "error" in upload_result:
            print(f"❌ Upload failed: {upload_result['error']}")
            return False
        
        print(f"✅ Document uploaded: {upload_result.get('filename', 'demo_document.md')}")
        if "chunks_created" in upload_result:
            print(f"   Chunks created: {upload_result['chunks_created']}")
        
        # Clean up sample document
        doc_path.unlink()
        
        # Demo conversations
        print("\n3. Running demo conversations...")
        
        demo_messages = [
            "Hello! What can you do?",
            "What documents do you have?",
            "What is the capital of France?",
            "Tell me about WhiteLabelRAG features",
            "Who created Python?",
            "What is the speed of light?",
            "List my files",
            "What time is it?",
            "Calculate 15 * 23 + 7"
        ]
        
        for i, message in enumerate(demo_messages, 1):
            print(f"\n📝 Demo {i}: {message}")
            print("-" * 30)
            
            response = self.send_message(message)
            
            if response.get("error"):
                print(f"❌ {response['text']}")
            else:
                print(f"🤖 {response.get('text', 'No response')}")
                
                sources = response.get("sources", [])
                if sources:
                    print(f"📚 Sources: {', '.join(sources)}")
            
            time.sleep(1)  # Brief pause between messages
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\n💡 Try the web interface at: http://localhost:5000")
        
        return True

def main():
    """Run the demo."""
    demo = WhiteLabelRAGDemo()
    success = demo.run_demo()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()