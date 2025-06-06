@echo off
REM Script to start the application using Docker Compose

echo Starting the application using Docker Compose...
docker-compose -f ..\docker-compose.yml up --build
