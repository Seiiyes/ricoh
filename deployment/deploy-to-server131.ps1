# =============================================================================
# DEPLOY SCRIPT - Ricoh App -> Servidor 192.168.91.131
# Ejecutar desde PowerShell en: c:\Users\juan.lizarazo\Desktop\ricoh
# Requiere: Posh-SSH instalado (Install-Module -Name Posh-SSH -Force)
# =============================================================================

param(
    [string]$ServerIP   = "192.168.91.131",
    [string]$Username   = "odootic",
    [string]$Password   = $env:REMOTE_SSH_PASS,
    [string]$RemoteDir  = "/home/odootic/ricoh-app",
    [string]$LocalDir   = $PSScriptRoot + "\.."
)

# Intentar cargar desde el archivo .env si no se ha definido password
if (-not $Password) {
    if (Test-Path "$LocalDir\.env") {
        Get-Content "$LocalDir\.env" | Foreach-Object {
            if ($_ -match "^REMOTE_SSH_PASS=(.*)") {
                $Password = $Matches[1].Trim().Trim('"').Trim("'")
            }
            if ($_ -match "^REMOTE_SSH_HOST=(.*)") {
                $ServerIP = $Matches[1].Trim().Trim('"').Trim("'")
            }
            if ($_ -match "^REMOTE_SSH_USER=(.*)") {
                $Username = $Matches[1].Trim().Trim('"').Trim("'")
            }
        }
    }
}

if (-not $Password) {
    Write-Error "❌ ERROR DE SEGURIDAD: La contraseña SSH no está configurada. Por favor crea un archivo '.env' en la raíz del proyecto y agrega REMOTE_SSH_PASS=TuContraseña"
    exit 1
}

# Importar módulo SSH
if (-not (Get-Module -ListAvailable -Name Posh-SSH)) {
    Write-Host "⚠️  Instalando Posh-SSH..." -ForegroundColor Yellow
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser
}
Import-Module Posh-SSH

$SecurePass = ConvertTo-SecureString $Password -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential($Username, $SecurePass)

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Ricoh Equipment Management - Deploy a $ServerIP" -ForegroundColor Cyan  
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- Conectar al servidor ---
Write-Host "🔗 Conectando al servidor..." -ForegroundColor Yellow
try {
    $Session = New-SSHSession -ComputerName $ServerIP -Credential $Cred -AcceptKey -Force
    Write-Host "✅ Conexión SSH establecida" -ForegroundColor Green
} catch {
    Write-Host "❌ Error de conexión SSH: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# --- Verificar Docker en el servidor ---
Write-Host "🐳 Verificando Docker..." -ForegroundColor Yellow
$DockerCheck = Invoke-SSHCommand -SessionId $Session.SessionId -Command "docker --version 2>/dev/null || echo 'NO_DOCKER'"
if ($DockerCheck.Output -match "NO_DOCKER") {
    Write-Host "  Docker no instalado. Instalando..." -ForegroundColor Yellow
    Invoke-SSHCommand -SessionId $Session.SessionId -Command "curl -fsSL https://get.docker.com | sudo sh; sudo usermod -aG docker $Username; sudo systemctl enable docker; sudo systemctl start docker" | Out-Null
    Write-Host "✅ Docker instalado" -ForegroundColor Green
} else {
    Write-Host "✅ $($DockerCheck.Output)" -ForegroundColor Green
}

# --- Crear directorio remoto ---
Write-Host "📁 Preparando directorio remoto..." -ForegroundColor Yellow
Invoke-SSHCommand -SessionId $Session.SessionId -Command "mkdir -p $RemoteDir" | Out-Null
Write-Host "✅ Directorio: $RemoteDir" -ForegroundColor Green

# --- Crear sesión SFTP ---
Write-Host "📤 Iniciando transferencia de archivos..." -ForegroundColor Yellow
$SftpSession = New-SFTPSession -ComputerName $ServerIP -Credential $Cred -AcceptKey -Force

# Función helper para subir archivos
function Upload-File {
    param($LocalPath, $RemotePath)
    try {
        $RemoteDir2 = Split-Path $RemotePath -Parent
        Invoke-SSHCommand -SessionId $Session.SessionId -Command "mkdir -p '$RemoteDir2'" | Out-Null
        Set-SFTPFile -SFTPSession $SftpSession -LocalFile $LocalPath -RemotePath $RemotePath -Overwrite
        Write-Host "  ✅ $LocalPath" -ForegroundColor DarkGreen
    } catch {
        Write-Host "  ⚠️  Error subiendo $LocalPath`: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Función para subir directorio completo
function Upload-Directory {
    param($LocalDirPath, $RemoteDirPath, [string[]]$Exclude = @())
    
    $items = Get-ChildItem -Path $LocalDirPath -Recurse -File | Where-Object {
        $relativePath = $_.FullName.Substring($LocalDirPath.Length + 1)
        $skip = $false
        foreach ($ex in $Exclude) {
            if ($relativePath -like "$ex*" -or $_.DirectoryName -like "*\$ex*") {
                $skip = $true
                break
            }
        }
        -not $skip
    }
    
    foreach ($item in $items) {
        $relativePath = $item.FullName.Substring($LocalDirPath.Length + 1).Replace('\', '/')
        $remotePath = "$RemoteDirPath/$relativePath"
        Upload-File -LocalPath $item.FullName -RemotePath $remotePath
    }
}

$LocalPath = (Resolve-Path $LocalDir).Path

# Subir archivos principales
Write-Host "  Subiendo backend..." -ForegroundColor Cyan
Upload-Directory -LocalDirPath "$LocalPath\backend" -RemoteDirPath "$RemoteDir/backend" -Exclude @("__pycache__", ".pytest_cache", "venv", ".env")

Write-Host "  Subiendo src (frontend)..." -ForegroundColor Cyan
Upload-Directory -LocalDirPath "$LocalPath\src" -RemoteDirPath "$RemoteDir/src"

Write-Host "  Subiendo archivos raíz..." -ForegroundColor Cyan
$rootFiles = @("package.json", "vite.config.ts", "tsconfig.json", "tsconfig.app.json", "index.html", "postcss.config.js", "eslint.config.js")
foreach ($f in $rootFiles) {
    if (Test-Path "$LocalPath\$f") {
        Upload-File -LocalPath "$LocalPath\$f" -RemotePath "$RemoteDir/$f"
    }
}

Write-Host "  Subiendo public..." -ForegroundColor Cyan
Upload-Directory -LocalDirPath "$LocalPath\public" -RemoteDirPath "$RemoteDir/public"

# Subir docker-compose específico para este servidor
Write-Host "  Subiendo docker-compose..." -ForegroundColor Cyan
Upload-File -LocalPath "$LocalPath\deployment\docker-compose.server131.yml" -RemotePath "$RemoteDir/docker-compose.yml"

# Subir script de instalación
Write-Host "  Subiendo script de instalación..." -ForegroundColor Cyan
Upload-File -LocalPath "$LocalPath\deployment\install-server131.sh" -RemotePath "$RemoteDir/install.sh"

Write-Host "✅ Archivos transferidos correctamente" -ForegroundColor Green

# --- Dar permisos y ejecutar instalación ---
Write-Host ""
Write-Host "🚀 Iniciando instalación en el servidor..." -ForegroundColor Yellow

$cmds = @(
    "chmod +x $RemoteDir/install.sh",
    "cd $RemoteDir && sudo docker compose down --remove-orphans 2>/dev/null || true",
    "cd $RemoteDir && sudo docker compose up --build -d 2>&1"
)

foreach ($cmd in $cmds) {
    Write-Host "  Ejecutando: $cmd" -ForegroundColor DarkGray
    $result = Invoke-SSHCommand -SessionId $Session.SessionId -Command $cmd -TimeOut 300
    if ($result.ExitStatus -ne 0) {
        Write-Host "  ⚠️  Exit code: $($result.ExitStatus)" -ForegroundColor Yellow
        Write-Host $result.Error -ForegroundColor Red
    } else {
        Write-Host $result.Output -ForegroundColor DarkGray
    }
}

# --- Esperar y verificar ---
Write-Host ""
Write-Host "⏳ Esperando que los servicios arranquen (45 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

$statusResult = Invoke-SSHCommand -SessionId $Session.SessionId -Command "cd $RemoteDir && sudo docker compose ps"
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Estado de los Contenedores" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host $statusResult.Output

$healthResult = Invoke-SSHCommand -SessionId $Session.SessionId -Command "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo 'NO_RESPONSE'"
Write-Host ""
if ($healthResult.Output -eq "200") {
    Write-Host "✅ Backend API saludable (HTTP 200)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend respondió: $($healthResult.Output) (puede necesitar más tiempo)" -ForegroundColor Yellow
}

# --- Cerrar sesiones ---
Remove-SFTPSession -SFTPSession $SftpSession | Out-Null
Remove-SSHSession -SessionId $Session.SessionId | Out-Null

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  ✅ DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  🌐 Frontend:  http://$ServerIP" -ForegroundColor White
Write-Host "  🔧 Backend:   http://$ServerIP`:8000" -ForegroundColor White
Write-Host "  📖 API Docs:  http://$ServerIP`:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Para ver logs en el servidor:" -ForegroundColor Gray
Write-Host "  ssh odootic@$ServerIP 'cd ~/ricoh-app && docker compose logs -f'" -ForegroundColor Gray
Write-Host ""
