@echo off
REM Development server startup script for Windows

echo 🚀 Starting WhiteLabelRAG development server...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check for GEMINI_API_KEY
if "%GEMINI_API_KEY%"=="" (
    if not exist ".env" (
        echo ❌ GEMINI_API_KEY not set and .env file not found.
        echo.
        echo 🔧 How to fix:
        echo 1. Set environment variable: set GEMINI_API_KEY=your_api_key_here
        echo 2. Or copy .env.example to .env and add your API key
        echo 3. Get API key from: https://makersuite.google.com/app/apikey
        pause
        exit /b 1
    )
    echo ⚠️ GEMINI_API_KEY not set as environment variable, checking .env file...
)

REM Set development environment
set FLASK_ENV=development
set FLASK_DEBUG=True

REM Create directories if they don't exist
if not exist "uploads" mkdir uploads
if not exist "chromadb_data" mkdir chromadb_data
if not exist "logs" mkdir logs

echo ✅ Environment ready
echo 🌐 Starting server on http://localhost:5000
echo 📝 Logs will be displayed below...
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Start the application
python run.py

pause