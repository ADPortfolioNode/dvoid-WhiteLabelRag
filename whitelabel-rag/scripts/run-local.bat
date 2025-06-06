@echo off
REM Script to start the application locally in development mode

REM Set required environment variables (example, adjust as needed)
set GEMINI_API_KEY=your_gemini_api_key_here
set FLASK_ENV=development
set SECRET_KEY=your_secret_key_here

echo Starting the application locally in development mode...
python ..\run.py
