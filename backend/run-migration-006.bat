@echo off
echo ========================================
echo MIGRATION 006: Add detailed counter fields
echo ========================================
echo.

call venv\Scripts\activate.bat
python apply_migration_006.py

pause
