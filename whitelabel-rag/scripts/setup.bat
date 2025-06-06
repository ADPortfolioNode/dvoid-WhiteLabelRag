@echo off
REM WhiteLabelRAG Setup Script for Windows

echo 🚀 Setting up WhiteLabelRAG...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "chromadb_data" mkdir chromadb_data
if not exist "logs" mkdir logs

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating environment file...
    copy .env.example .env
    
    echo 🔑 Generating secure SECRET_KEY...
    for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set GENERATED_SECRET=%%i
    
    echo 📝 Updating .env file with generated SECRET_KEY...
    powershell -Command "(Get-Content .env) -replace 'SECRET_KEY=generate_with_python_secrets_token_urlsafe_32', 'SECRET_KEY=%GENERATED_SECRET%' | Set-Content .env"
    
    echo.
    echo ✅ Generated and set SECRET_KEY: %GENERATED_SECRET%
    echo.
    echo 📝 IMPORTANT: You need to set your GEMINI_API_KEY!
    echo.
    echo Option 1 - Set as environment variable:
    echo   set GEMINI_API_KEY=your_api_key_here
    echo.
    echo Option 2 - Add to .env file:
    echo   Edit .env file and uncomment/set GEMINI_API_KEY=your_api_key_here
    echo.
    echo Get your API key from: https://makersuite.google.com/app/apikey
    echo.
)

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your GEMINI_API_KEY
echo 2. Activate virtual environment: venv\Scripts\activate.bat
echo 3. Run the application: python run.py
echo 4. Open http://localhost:5000 in your browser
echo.
echo For Docker deployment:
echo 1. Set GEMINI_API_KEY in .env file
echo 2. Run: docker-compose up -d

pause