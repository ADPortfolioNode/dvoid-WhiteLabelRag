#!/usr/bin/env python3
"""
Docker deployment test script for WhiteLabelRAG
"""

import os
import sys
import time
import requests
import subprocess
import json
from pathlib import Path

def print_status(message):
    print(f"🔍 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def run_command(command, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Check if Docker is available."""
    print_status("Checking Docker installation...")
    
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print_error("Docker is not installed or not running")
        return False
    
    success, stdout, stderr = run_command("docker-compose --version")
    if not success:
        print_error("Docker Compose is not installed")
        return False
    
    print_success("Docker and Docker Compose are available")
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    print_status("Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print_warning(".env file not found")
        return False
    
    with open(env_file) as f:
        content = f.read()
    
    if "GEMINI_API_KEY=" not in content or "GEMINI_API_KEY=$" in content:
        print_warning("GEMINI_API_KEY not properly set in .env file")
        return False
    
    print_success("Environment configuration is valid")
    return True

def test_build():
    """Test building the Docker image."""
    print_status("Testing Docker image build...")
    
    success, stdout, stderr = run_command("docker-compose build", capture_output=False)
    if not success:
        print_error("Failed to build Docker image")
        print(f"Error: {stderr}")
        return False
    
    print_success("Docker image built successfully")
    return True

def test_deployment():
    """Test deploying the application."""
    print_status("Testing application deployment...")
    
    # Start the application
    success, stdout, stderr = run_command("docker-compose up -d")
    if not success:
        print_error("Failed to start application")
        print(f"Error: {stderr}")
        return False
    
    print_success("Application started successfully")
    
    # Wait for application to be ready
    print_status("Waiting for application to be ready...")
    time.sleep(30)
    
    return True

def test_health_check():
    """Test application health check."""
    print_status("Testing application health...")
    
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:5000/health", timeout=10)
            if response.status_code == 200:
                print_success("Application health check passed")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            print_status(f"Health check attempt {i+1}/{max_retries} failed, retrying...")
            time.sleep(5)
    
    print_error("Application health check failed")
    return False

def test_api_endpoints():
    """Test basic API endpoints."""
    print_status("Testing API endpoints...")
    
    endpoints = [
        ("/", "GET", "Main page"),
        ("/health", "GET", "Health check"),
        ("/api/health", "GET", "API health check"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            url = f"http://localhost:5000{endpoint}"
            response = requests.request(method, url, timeout=10)
            
            if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                print_success(f"{description}: {response.status_code}")
            else:
                print_warning(f"{description}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print_error(f"{description}: {str(e)}")
    
    return True

def test_container_logs():
    """Check container logs for errors."""
    print_status("Checking container logs...")
    
    success, stdout, stderr = run_command("docker-compose logs --tail=50 whitelabel-rag")
    if success and stdout:
        # Check for common error patterns
        error_patterns = ["ERROR", "CRITICAL", "Exception", "Traceback"]
        lines = stdout.split('\n')
        
        errors_found = []
        for line in lines:
            for pattern in error_patterns:
                if pattern in line and "Health check" not in line:
                    errors_found.append(line.strip())
        
        if errors_found:
            print_warning("Found potential errors in logs:")
            for error in errors_found[-5:]:  # Show last 5 errors
                print(f"  {error}")
        else:
            print_success("No critical errors found in logs")
    
    return True

def cleanup():
    """Clean up test deployment."""
    print_status("Cleaning up test deployment...")
    
    success, stdout, stderr = run_command("docker-compose down")
    if success:
        print_success("Test deployment cleaned up")
    else:
        print_warning("Failed to clean up test deployment")

def main():
    """Main test function."""
    print("🐳 WhiteLabelRAG Docker Deployment Test")
    print("=" * 50)
    
    # Change to project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    tests = [
        ("Docker Installation", check_docker),
        ("Environment Configuration", check_env_file),
        ("Docker Build", test_build),
        ("Application Deployment", test_deployment),
        ("Health Check", test_health_check),
        ("API Endpoints", test_api_endpoints),
        ("Container Logs", test_container_logs),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Cleanup
    cleanup()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
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
        print_success("🎉 All tests passed! Docker deployment is ready.")
        return 0
    else:
        print_error("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())