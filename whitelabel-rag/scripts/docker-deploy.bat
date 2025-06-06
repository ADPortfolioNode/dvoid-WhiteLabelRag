@echo off
REM WhiteLabelRAG Docker Deployment Script for Windows

setlocal enabledelayedexpansion

REM Colors (limited in Windows CMD)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Functions
:print_status
echo %INFO% %~1
goto :eof

:print_success
echo %SUCCESS% %~1
goto :eof

:print_warning
echo %WARNING% %~1
goto :eof

:print_error
echo %ERROR% %~1
goto :eof

REM Check if Docker is installed
:check_docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker Compose is not installed. Please install Docker Desktop first."
    exit /b 1
)

call :print_success "Docker and Docker Compose are installed"
goto :eof

REM Check environment file
:check_env
if not exist .env (
    call :print_warning ".env file not found. Creating from template..."
    copy .env.example .env >nul
    call :print_warning "Please edit .env file and add your GEMINI_API_KEY"
    exit /b 1
)

findstr /C:"GEMINI_API_KEY=" .env | findstr /V /C:"GEMINI_API_KEY=$" >nul
if errorlevel 1 (
    call :print_warning "GEMINI_API_KEY not set in .env file"
    exit /b 1
)

call :print_success "Environment configuration found"
goto :eof

REM Build images
:build_images
call :print_status "Building Docker images..."

if "%~1"=="dev" (
    docker-compose -f docker-compose.dev.yml build
) else (
    docker-compose build
)

if errorlevel 1 (
    call :print_error "Failed to build images"
    exit /b 1
)

call :print_success "Images built successfully"
goto :eof

REM Deploy application
:deploy
set mode=%~1
call :print_status "Deploying WhiteLabelRAG in %mode% mode..."

if "%mode%"=="dev" (
    docker-compose -f docker-compose.dev.yml up -d
) else if "%mode%"=="nginx" (
    docker-compose --profile nginx up -d
) else (
    docker-compose up -d
)

if errorlevel 1 (
    call :print_error "Deployment failed"
    exit /b 1
)

call :print_success "Deployment completed"
goto :eof

REM Check deployment status
:check_status
call :print_status "Checking deployment status..."

REM Wait a moment for containers to start
timeout /t 5 /nobreak >nul

if "%~1"=="dev" (
    docker-compose -f docker-compose.dev.yml ps
) else (
    docker-compose ps
)

REM Check health
call :print_status "Checking application health..."
timeout /t 10 /nobreak >nul

curl -f http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    call :print_warning "Application health check failed. Check logs with:"
    echo   docker-compose logs -f whitelabel-rag
) else (
    call :print_success "Application is healthy and responding"
    call :print_success "Access the application at: http://localhost:5000"
)
goto :eof

REM Show usage
:usage
echo WhiteLabelRAG Docker Deployment Script
echo.
echo Usage: %~nx0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo   build [dev]         Build Docker images
echo   deploy [dev^|nginx]  Deploy the application
echo   status [dev]        Check deployment status
echo   logs [dev]          Show application logs
echo   stop [dev]          Stop the application
echo   restart [dev]       Restart the application
echo   clean               Clean up containers and images
echo   help                Show this help message
echo.
echo Options:
echo   dev                 Use development configuration
echo   nginx               Deploy with Nginx reverse proxy
echo.
echo Examples:
echo   %~nx0 deploy              # Deploy in production mode
echo   %~nx0 deploy dev          # Deploy in development mode
echo   %~nx0 deploy nginx        # Deploy with Nginx proxy
echo   %~nx0 logs                # Show production logs
echo   %~nx0 logs dev            # Show development logs
goto :eof

REM Show logs
:show_logs
if "%~1"=="dev" (
    docker-compose -f docker-compose.dev.yml logs -f
) else (
    docker-compose logs -f
)
goto :eof

REM Stop application
:stop_app
call :print_status "Stopping WhiteLabelRAG..."

if "%~1"=="dev" (
    docker-compose -f docker-compose.dev.yml down
) else (
    docker-compose down
    docker-compose --profile nginx down
)

call :print_success "Application stopped"
goto :eof

REM Restart application
:restart_app
call :print_status "Restarting WhiteLabelRAG..."

if "%~1"=="dev" (
    docker-compose -f docker-compose.dev.yml restart
) else (
    docker-compose restart
)

call :print_success "Application restarted"
goto :eof

REM Clean up
:cleanup
call :print_status "Cleaning up Docker resources..."

REM Stop all containers
docker-compose down >nul 2>&1
docker-compose -f docker-compose.dev.yml down >nul 2>&1
docker-compose --profile nginx down >nul 2>&1

REM Remove unused images
docker image prune -f

REM Remove unused volumes (ask for confirmation)
set /p "confirm=Remove unused volumes? This will delete data! (y/N): "
if /i "%confirm%"=="y" (
    docker volume prune -f
    call :print_warning "Volumes removed"
)

call :print_success "Cleanup completed"
goto :eof

REM Main script
:main
set command=%~1
set option=%~2

REM Change to script directory
cd /d "%~dp0\.."

if "%command%"=="build" (
    call :check_docker
    if errorlevel 1 exit /b 1
    call :build_images %option%
) else if "%command%"=="deploy" (
    call :check_docker
    if errorlevel 1 exit /b 1
    call :check_env
    if errorlevel 1 (
        call :print_error "Please configure .env file first"
        exit /b 1
    )
    call :build_images %option%
    if errorlevel 1 exit /b 1
    call :deploy %option%
    if errorlevel 1 exit /b 1
    call :check_status %option%
) else if "%command%"=="status" (
    call :check_status %option%
) else if "%command%"=="logs" (
    call :show_logs %option%
) else if "%command%"=="stop" (
    call :stop_app %option%
) else if "%command%"=="restart" (
    call :restart_app %option%
) else if "%command%"=="clean" (
    call :cleanup
) else if "%command%"=="help" (
    call :usage
) else if "%command%"=="--help" (
    call :usage
) else if "%command%"=="-h" (
    call :usage
) else (
    call :print_error "Unknown command: %command%"
    echo.
    call :usage
    exit /b 1
)

goto :eof

REM Run main function
call :main %*