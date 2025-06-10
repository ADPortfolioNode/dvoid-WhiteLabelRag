@echo off
REM Test script for Google Internet Search integration
REM This script runs test_internet_search.py to verify the Google API key configuration

echo Testing Google Internet Search Integration...
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found in PATH. Please install Python or add it to your PATH.
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found. 
    echo Make sure you have set GOOGLE_API_KEY and INTERNET_SEARCH_ENGINE_ID in your environment.
    echo.
)

REM Run the test script
python scripts\test_internet_search.py %*

REM Check the result
if %ERRORLEVEL% neq 0 (
    echo.
    echo Test failed. Please check the configuration and try again.
    exit /b 1
) else (
    echo.
    echo Test completed successfully!
    exit /b 0
)
