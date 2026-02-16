@echo off
REM Ricoh Multi-Fleet Governance Suite - Docker Startup Script

echo ========================================
echo Ricoh Multi-Fleet Governance Suite
echo Docker Compose Startup
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running...
echo.

REM Stop any existing containers
echo Stopping existing containers...
docker-compose down

echo.
echo Building and starting services...
echo - PostgreSQL Database
echo - Adminer (Database UI)
echo - FastAPI Backend
echo - React Frontend
echo.

REM Start services
docker-compose up --build -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo.
echo Frontend:     http://localhost:5173
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Database UI:  http://localhost:8080
echo.
echo Database Credentials:
echo   Server:   postgres
echo   Database: ricoh_fleet
echo   User:     ricoh_admin
echo   Password: ricoh_secure_2024
echo.
echo ========================================
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo.

pause
