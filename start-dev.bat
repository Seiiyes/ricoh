@echo off
REM Ricoh Multi-Fleet Governance Suite - Development Startup Script for Windows

echo Starting Ricoh Multi-Fleet Governance Suite...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed. Please install Node.js 16 or higher.
    exit /b 1
)

REM Start Backend
echo Starting Backend API...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
if not exist "venv\.installed" (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    type nul > venv\.installed
)

REM Create .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo Created .env file with default settings
)

REM Start backend
echo Starting FastAPI server on http://localhost:8000...
start /B python main.py
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
echo.
echo Starting Frontend...

REM Create .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env
    echo Created frontend .env file
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

REM Start frontend
echo Starting Vite dev server on http://localhost:5173...
start /B npm run dev

echo.
echo Services started successfully!
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C to stop all services
echo.

pause
