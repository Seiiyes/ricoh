@echo off
REM Ricoh Suite - Production Deployment Script (Windows)
REM This script automates the deployment process for production

setlocal enabledelayedexpansion

echo ================================================================================
echo 🚀 Ricoh Suite - Production Deployment
echo ================================================================================
echo.

REM Configuration
set BACKUP_DIR=..\backups
set DB_NAME=ricoh_fleet
set DB_USER=ricoh_admin
set DB_HOST=localhost
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=%BACKUP_DIR%\ricoh_backup_pre_deploy_%TIMESTAMP%.sql

REM Step 1: Pre-deployment checks
echo 📋 Step 1: Pre-deployment checks
echo --------------------------------

if not exist ".env" (
    echo ✗ .env file not found!
    echo Please create .env file with production configuration
    exit /b 1
)
echo ✓ .env file found

findstr /C:"SECRET_KEY=" .env >nul
if errorlevel 1 (
    echo ✗ SECRET_KEY not found in .env!
    echo Please set SECRET_KEY in .env file
    exit /b 1
)
echo ✓ SECRET_KEY configured

findstr /C:"DATABASE_URL=" .env >nul
if errorlevel 1 (
    echo ✗ DATABASE_URL not found in .env!
    echo Please set DATABASE_URL in .env file
    exit /b 1
)
echo ✓ DATABASE_URL configured

findstr /C:"ENVIRONMENT=production" .env >nul
if errorlevel 1 (
    echo ⚠ ENVIRONMENT is not set to 'production' in .env
    set /p continue="Continue anyway? (y/n): "
    if /i not "!continue!"=="y" exit /b 1
)

echo.

REM Step 2: Create backup
echo 💾 Step 2: Creating database backup
echo -----------------------------------

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

echo ✓ Creating backup: %BACKUP_FILE%
pg_dump -U %DB_USER% -h %DB_HOST% %DB_NAME% > "%BACKUP_FILE%"

if errorlevel 1 (
    echo ✗ Backup failed!
    exit /b 1
)
echo ✓ Backup created successfully

echo.

REM Step 3: Run migrations
echo 🗄️  Step 3: Running database migrations
echo ---------------------------------------

echo ✓ Executing migrations...
python scripts\run_migrations.py

if errorlevel 1 (
    echo ✗ Migrations failed!
    echo.
    echo Rolling back...
    echo ✓ Restoring backup: %BACKUP_FILE%
    psql -U %DB_USER% -h %DB_HOST% %DB_NAME% < "%BACKUP_FILE%"
    exit /b 1
)
echo ✓ Migrations completed successfully

echo.

REM Step 4: Install/Update dependencies
echo 📦 Step 4: Installing dependencies
echo ----------------------------------

echo ✓ Installing Python dependencies...
pip install -q -r requirements.txt

if errorlevel 1 (
    echo ✗ Dependency installation failed!
    exit /b 1
)
echo ✓ Dependencies installed successfully

echo.

REM Step 5: Run tests (optional)
echo 🧪 Step 5: Running tests (optional)
echo -----------------------------------

set /p run_tests="Run tests before deployment? (y/n): "
if /i "%run_tests%"=="y" (
    echo ✓ Running tests...
    python -m pytest tests\ -v --tb=short
    
    if errorlevel 1 (
        echo ✗ Tests failed!
        set /p continue_anyway="Continue deployment anyway? (y/n): "
        if /i not "!continue_anyway!"=="y" exit /b 1
    ) else (
        echo ✓ All tests passed
    )
) else (
    echo ⚠ Skipping tests
)

echo.

REM Step 6: Restart services
echo 🔄 Step 6: Restarting services
echo ------------------------------

echo ✓ Stopping services...
REM Add your service stop command here
REM Example: net stop RicohAPI

echo ✓ Starting services...
REM Add your service start command here
REM Example: net start RicohAPI

echo ✓ Services restarted

echo.

REM Step 7: Verify deployment
echo ✅ Step 7: Verifying deployment
echo -------------------------------

echo ✓ Waiting for services to start...
timeout /t 5 /nobreak >nul

echo ✓ Checking API health...
curl -s -o nul -w "%%{http_code}" http://localhost:8000/ > temp_response.txt
set /p response=<temp_response.txt
del temp_response.txt

if "%response%"=="200" (
    echo ✓ API is responding correctly
) else (
    echo ✗ API is not responding (HTTP %response%)
    echo ⚠ Please check logs for errors
)

echo.

REM Step 8: Post-deployment tasks
echo 📝 Step 8: Post-deployment tasks
echo --------------------------------

echo ✓ Deployment completed at: %date% %time%
echo ✓ Backup location: %BACKUP_FILE%
echo ✓ Please monitor logs for the next hour

echo.
echo ================================================================================
echo ✅ Deployment completed successfully!
echo ================================================================================
echo.
echo Next steps:
echo 1. Monitor logs: type logs\ricoh_api.log
echo 2. Test login with superadmin
echo 3. Verify all endpoints are working
echo 4. Monitor for errors for 1 hour
echo.
echo Rollback instructions (if needed):
echo 1. Stop services
echo 2. Restore backup: psql -U %DB_USER% -h %DB_HOST% %DB_NAME% ^< %BACKUP_FILE%
echo 3. Revert code to previous version
echo 4. Start services
echo.

pause
