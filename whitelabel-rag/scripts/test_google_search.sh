#!/bin/bash
# Test script for Google Internet Search integration
# This script runs test_internet_search.py to verify the Google API key configuration

echo "Testing Google Internet Search Integration..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3 or add it to your PATH."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found."
    echo "Make sure you have set GOOGLE_API_KEY and INTERNET_SEARCH_ENGINE_ID in your environment."
    echo
fi

# Run the test script
python3 scripts/test_internet_search.py "$@"

# Check the result
if [ $? -ne 0 ]; then
    echo
    echo "Test failed. Please check the configuration and try again."
    exit 1
else
    echo
    echo "Test completed successfully!"
    exit 0
fi
