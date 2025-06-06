@echo off
cd %~dp0\..
cd whitelabel-rag
echo Starting critical-path testing for WhiteLabelRAG Docker build...


echo.
echo Step 1: Checking Docker container status...
docker-compose ps
if errorlevel 1 (
    echo ERROR: Failed to get Docker container status.
    goto end
)
echo Docker containers status checked successfully.

echo.
echo Step 2: Verifying web interface accessibility at http://localhost:5000 ...
curl --fail http://localhost:5000 > nul 2>&1
if errorlevel 1 (
    echo ERROR: Web interface is not accessible at http://localhost:5000
    goto end
)
echo Web interface is accessible.

echo.
echo Step 3: Checking health endpoint at http://localhost:5000/health ...
curl --fail http://localhost:5000/health > nul 2>&1
if errorlevel 1 (
    echo ERROR: Health endpoint is not accessible or returned error.
    goto end
)
echo Health endpoint is accessible and returned success.

echo.
echo Step 4: Viewing recent logs for whitelabel-rag container (last 50 lines)...
docker-compose logs --tail=50 whitelabel-rag

echo.
echo Step 5: Please manually test basic application functionality through the web interface.

:end
echo.
echo Critical-path testing completed.
pause
