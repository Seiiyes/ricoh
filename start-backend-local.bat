@echo off
echo Iniciando backend localmente (fuera de Docker)...
echo.

cd backend

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias (esto puede tardar varios minutos)...
pip install --upgrade pip >nul 2>&1
pip install fastapi==0.115.0 >nul 2>&1
pip install "uvicorn[standard]==0.32.0" >nul 2>&1
pip install pydantic==2.10.0 >nul 2>&1
pip install "pydantic[email]==2.10.0" >nul 2>&1
pip install python-multipart==0.0.12 >nul 2>&1
pip install sqlalchemy==2.0.36 >nul 2>&1
echo Instalando psycopg2-binary (puede tardar)...
pip install psycopg2-binary==2.9.11 --only-binary :all:
pip install alembic==1.14.0 >nul 2>&1
pip install websockets==14.1 >nul 2>&1
pip install email-validator==2.1.0 >nul 2>&1
pip install cryptography==42.0.5 >nul 2>&1
pip install beautifulsoup4==4.12.3 >nul 2>&1
pip install requests==2.31.0 >nul 2>&1
pip install dnspython==2.6.1 >nul 2>&1

echo.
echo Dependencias instaladas correctamente
echo.

REM Configurar variables de entorno
set DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet
set DEMO_MODE=false
set API_HOST=0.0.0.0
set API_PORT=8000
set CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
set SECRET_KEY=ricoh-secret-key-change-in-production

REM Iniciar servidor
echo Backend corriendo en http://localhost:8000
echo Presiona Ctrl+C para detener
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
