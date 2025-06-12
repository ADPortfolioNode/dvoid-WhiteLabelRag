@echo off
REM startapp.bat - Restart the WhiteLabelRAG Docker app using docker-entrypoint.sh

REM Change directory to the script location
cd /d "%~dp0whitelabel-rag"

REM Set the DOCKER_ACTION environment variable to restart
set DOCKER_ACTION=restart

REM Run the entrypoint script using WSL/bash
bash docker-entrypoint.sh
 