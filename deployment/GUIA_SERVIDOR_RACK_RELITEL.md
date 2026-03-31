# Guía de Configuración - Servidor Rack Físico 24/7
## Ricoh Equipment Management - RELITELTDA

**Red actual**: 192.168.91.0/24  
**Gateway**: 192.168.91.1  
**Tu PC**: 192.168.91.34 (TIC0264) - SIN permisos de administrador  
**Servidor Rack**: 192.168.91.100 (a configurar)

---

## 🔴 IMPORTANTE: División de Tareas

Esta guía está dividida en dos secciones claramente marcadas:

- **🏢 EN EL RACK** = Requiere acceso físico al servidor (monitor + teclado conectados)
- **💻 DESDE TU PC** = Puedes hacerlo desde tu escritorio (192.168.91.34) sin permisos de admin

---

# PARTE 1: CONFIGURACIÓN EN EL RACK (Acceso Físico Requerido)

## 🏢 Fase 1: Preparación Física del Servidor Rack

**Ubicación**: En el cuarto de servidores, frente al rack  
**Necesitas**: Monitor, teclado, mouse conectados al servidor rack

### 1.1 Verificación de Hardware

Antes de comenzar, verifica físicamente:

- [ ] Servidor rack conectado a la corriente
- [ ] Cable de red conectado al switch/router de la red 192.168.91.x
- [ ] Monitor conectado al puerto VGA/HDMI del servidor
- [ ] Teclado USB conectado al servidor
- [ ] Mouse USB conectado (opcional)
- [ ] UPS conectado (recomendado para protección)
- [ ] Servidor encendido y con Ubuntu Server instalado

### 1.2 Requisitos Mínimos Verificados

- [ ] **CPU**: 4 cores o más
- [ ] **RAM**: 8 GB mínimo (16 GB recomendado)
- [ ] **Disco**: 50 GB SSD mínimo (100 GB recomendado)
- [ ] **Red**: Puerto Ethernet conectado a red 192.168.91.x

---

## 🏢 Fase 2: Configuración Inicial del Servidor (EN EL RACK)

### 2.1 Iniciar Sesión en el Servidor

**Ubicación**: Frente al servidor rack con monitor y teclado conectados

1. Enciende el servidor si está apagado
2. Espera a que aparezca la pantalla de login de Ubuntu Server
3. Inicia sesión con el usuario creado durante la instalación de Ubuntu Server
   - Usuario: (el que creaste durante la instalación)
   - Contraseña: (la que configuraste durante la instalación)

**Nota**: Si no recuerdas el usuario/contraseña, necesitarás resetear desde el modo recovery de Ubuntu.

### 2.2 Identificar Interfaz de Red

```bash
# Ver interfaces de red disponibles
ip a

# Busca la interfaz activa (puede ser: eth0, ens18, ens33, enp0s3, etc.)
# Anota el nombre de la interfaz que tiene conexión
```

### 2.3 Configurar IP Estática

```bash
# Editar configuración de red
sudo nano /etc/netplan/00-installer-config.yaml
```

**Contenido del archivo** (ajusta el nombre de la interfaz según el paso anterior):

```yaml
network:
  version: 2
  ethernets:
    ens18:  # CAMBIAR por tu interfaz (eth0, ens33, etc.)
      addresses:
        - 192.168.91.100/24  # IP estática del servidor
      routes:
        - to: default
          via: 192.168.91.1  # Gateway de tu red
      nameservers:
        addresses:
          - 11.0.20.10      # DNS primario de RELITELTDA
          - 192.168.91.1    # DNS secundario (gateway)
          - 8.8.8.8         # DNS terciario (Google)
```

**Aplicar configuración:**

```bash
# Aplicar cambios
sudo netplan apply

# Verificar que la IP está configurada
ip a

# Probar conectividad
ping 192.168.91.1
ping 8.8.8.8
```

### 2.4 Actualizar Sistema

```bash
# Actualizar paquetes
sudo apt update
sudo apt upgrade -y
```

### 2.5 Instalar y Configurar SSH

```bash
# Instalar OpenSSH Server
sudo apt install -y openssh-server

# Habilitar SSH al inicio
sudo systemctl enable ssh
sudo systemctl start ssh

# Verificar estado
sudo systemctl status ssh

# Ver IP del servidor
ip a | grep "inet 192.168.91"
```

### 2.6 Configurar Firewall Básico

```bash
# Instalar UFW si no está instalado
sudo apt install -y ufw

# Permitir SSH (CRÍTICO: hacer esto ANTES de habilitar el firewall)
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw enable

# Verificar reglas
sudo ufw status verbose
```

### 2.7 Crear Usuario de Administración (Opcional pero Recomendado)

**Propósito**: Crear un usuario específico para que tú puedas administrar el servidor remotamente

```bash
# Crear usuario para administración remota
sudo adduser ricoh-admin

# Te pedirá:
# - Nueva contraseña (elige una segura y guárdala)
# - Confirmar contraseña
# - Información adicional (puedes dejar en blanco presionando Enter)

# Agregar a grupo sudo (para poder usar sudo remotamente)
sudo usermod -aG sudo ricoh-admin

# Verificar que se creó correctamente
id ricoh-admin
```

**IMPORTANTE**: Anota este usuario y contraseña, los usarás para conectarte desde tu PC.

---

## 🏢 Fase 3: Verificación Final en el Rack

### 3.1 Verificar Conectividad

```bash
# Ver IP asignada
ip a | grep "inet 192.168.91"

# Deberías ver: inet 192.168.91.100/24

# Probar conectividad a internet
ping -c 4 8.8.8.8

# Probar DNS
ping -c 4 google.com

# Verificar que SSH está corriendo
sudo systemctl status ssh

# Deberías ver: "active (running)"
```

### 3.2 Anotar Información Importante

Antes de desconectar el monitor y teclado, anota:

- ✅ IP del servidor: **192.168.91.100**
- ✅ Usuario para SSH: **ricoh-admin** (o el que creaste)
- ✅ Contraseña: **[anótala en lugar seguro]**
- ✅ SSH está activo: **Sí**
- ✅ Firewall permite SSH: **Sí (puerto 22)**

### 3.3 Desconectar Monitor y Teclado

Una vez verificado todo:

1. Cierra sesión: `exit` o `logout`
2. Desconecta el monitor del servidor
3. Desconecta el teclado del servidor
4. El servidor seguirá corriendo 24/7

**El servidor ahora está listo para administración remota desde tu PC.**

---

# PARTE 2: ADMINISTRACIÓN DESDE TU PC (Sin Permisos de Admin)

## 💻 Fase 4: Conexión SSH desde tu PC Windows

**Ubicación**: Tu escritorio (TIC0264 - 192.168.91.34)  
**Herramientas**: PowerShell (no requiere permisos de admin) o Git Bash

### 4.1 Abrir PowerShell

1. Presiona `Windows + R`
2. Escribe: `powershell`
3. Presiona Enter

**Nota**: No necesitas "Ejecutar como administrador"

### 4.2 Probar Conectividad al Servidor

```powershell
# Probar ping al servidor
ping 192.168.91.100

# Deberías ver respuestas como:
# Respuesta desde 192.168.91.100: bytes=32 tiempo<1ms TTL=64
```

Si el ping funciona, continúa. Si no funciona:
- Verifica que el servidor está encendido
- Verifica que el cable de red está conectado
- Pide ayuda al administrador de red

### 4.3 Primera Conexión SSH

```powershell
# Conectar al servidor
ssh ricoh-admin@192.168.91.100

# Te preguntará:
# "Are you sure you want to continue connecting (yes/no/[fingerprint])?"
# Escribe: yes
# Presiona Enter

# Luego te pedirá la contraseña del usuario ricoh-admin
# Escríbela (no se verá mientras escribes) y presiona Enter
```

**¡Felicidades!** Si ves el prompt del servidor (algo como `ricoh-admin@servidor:~$`), estás conectado.

### 4.4 Comandos Básicos en el Servidor (via SSH)

```bash
# Ver en qué directorio estás
pwd

# Listar archivos
ls -la

# Ver uso de disco
df -h

# Ver memoria
free -h

# Ver procesos
top
# (presiona 'q' para salir)

# Salir de la sesión SSH
exit
```

---

## 💻 Fase 5: Configurar Acceso SSH Simplificado (Opcional)

### 5.1 Generar Clave SSH (Sin Permisos de Admin)

**Propósito**: Conectarte sin escribir contraseña cada vez

```powershell
# En PowerShell de tu PC
# Generar par de claves SSH
ssh-keygen -t ed25519 -C "juan.lizarazo@reliteltda.local"

# Te preguntará:
# "Enter file in which to save the key": Presiona Enter (usa ubicación por defecto)
# "Enter passphrase": Presiona Enter (sin contraseña) o escribe una contraseña adicional
# "Enter same passphrase again": Presiona Enter o repite la contraseña

# Deberías ver:
# "Your identification has been saved in C:\Users\juan.lizarazo\.ssh\id_ed25519"
# "Your public key has been saved in C:\Users\juan.lizarazo\.ssh\id_ed25519.pub"
```

### 5.2 Copiar Clave al Servidor

```powershell
# Copiar clave pública al servidor
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh ricoh-admin@192.168.91.100 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

# Te pedirá la contraseña de ricoh-admin una última vez
```

### 5.3 Probar Conexión sin Contraseña

```powershell
# Ahora puedes conectar sin contraseña
ssh ricoh-admin@192.168.91.100

# Debería conectar directamente sin pedir contraseña
```

### 5.4 Crear Alias para Conexión Rápida

```powershell
# Crear archivo de configuración SSH
notepad $env:USERPROFILE\.ssh\config

# Si dice que el archivo no existe, acepta crearlo
```

**Contenido del archivo:**

```
Host ricoh-server
    HostName 192.168.91.100
    User ricoh-admin
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Guarda el archivo (Ctrl+S) y cierra el Notepad.

**Ahora puedes conectar simplemente con:**

```powershell
ssh ricoh-server
```

---

## 💻 Fase 6: Transferir Archivos desde tu PC al Servidor

### 6.1 Copiar Script de Setup

**Opción A: Si tienes el repositorio en tu PC**

```powershell
# Desde PowerShell en tu PC, en el directorio del proyecto
cd C:\ruta\a\tu\proyecto

# Copiar script al servidor
scp deployment/setup-ubuntu-server.sh ricoh-admin@192.168.91.100:~/

# Copiar toda la carpeta deployment
scp -r deployment ricoh-admin@192.168.91.100:~/
```

**Opción B: Copiar archivo individual**

```powershell
# Copiar un archivo específico
scp C:\ruta\al\archivo.txt ricoh-admin@192.168.91.100:~/
```

### 6.2 Verificar que se Copió

```powershell
# Conectar al servidor
ssh ricoh-server

# Listar archivos
ls -la

# Deberías ver: setup-ubuntu-server.sh
```

---

## 💻 Fase 7: Instalación Automatizada (Desde tu PC via SSH)

**Todo esto lo haces desde tu PC, conectado via SSH al servidor**

### 7.1 Conectar al Servidor

```powershell
# Desde PowerShell en tu PC
ssh ricoh-server
```

### 7.2 Ejecutar Script de Setup

```bash
# Ahora estás en el servidor (via SSH)
# Dar permisos de ejecución al script
chmod +x setup-ubuntu-server.sh

# Ejecutar como root
sudo bash setup-ubuntu-server.sh

# Te pedirá tu contraseña de ricoh-admin
# El script tardará 5-10 minutos
```

**El script instalará automáticamente:**
- ✅ Docker y Docker Compose
- ✅ Nginx
- ✅ Certbot (para SSL)
- ✅ Firewall configurado
- ✅ Usuario 'ricoh' para deployment
- ✅ Systemd service
- ✅ Log rotation
- ✅ Optimizaciones del kernel

**Espera a que termine. Verás mensajes en verde (✓) cuando cada paso se complete.**

---

## 💻 Fase 8: Preparar Aplicación (Desde tu PC via SSH)

### 8.1 Crear Directorio de Aplicación

```bash
# Conectado al servidor via SSH
sudo mkdir -p /opt/ricoh
sudo chown -R ricoh:ricoh /opt/ricoh
```

### 8.2 Transferir Código de la Aplicación

**Opción A: Clonar desde Git (si el repositorio es accesible)**

```bash
# En el servidor via SSH
cd /opt/ricoh
sudo git clone https://github.com/tu-org/ricoh-equipment-management.git .
sudo chown -R ricoh:ricoh /opt/ricoh
```

**Opción B: Copiar desde tu PC**

Desde otra ventana de PowerShell en tu PC (sin cerrar la sesión SSH):

```powershell
# Comprimir el proyecto (excluyendo node_modules, .git, etc.)
# Asumiendo que estás en el directorio del proyecto

# Copiar archivos necesarios al servidor
scp -r backend ricoh-admin@192.168.91.100:/opt/ricoh/
scp -r frontend ricoh-admin@192.168.91.100:/opt/ricoh/
scp -r deployment ricoh-admin@192.168.91.100:/opt/ricoh/
scp docker-compose.yml ricoh-admin@192.168.91.100:/opt/ricoh/
scp package.json ricoh-admin@192.168.91.100:/opt/ricoh/
```

### 8.3 Generar Claves de Seguridad

```bash
# En el servidor via SSH
cd /opt/ricoh

# Generar ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Copiar el resultado y guardarlo en un archivo de texto en tu PC

# Generar SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Copiar el resultado y guardarlo

# Generar POSTGRES_PASSWORD
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24))"

# Copiar el resultado y guardarlo

# Generar REDIS_PASSWORD
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(24))"

# Copiar el resultado y guardarlo
```

**IMPORTANTE**: Guarda todas estas claves en un archivo de texto en tu PC (en un lugar seguro).

### 8.4 Configurar Variables de Entorno

```bash
# En el servidor via SSH
cd /opt/ricoh

# Copiar archivo de ejemplo
cp deployment/.env.production.example .env.production

# Editar configuración
nano .env.production
```

**Configuración mínima** (usa las claves que generaste arriba):

```bash
# Database
POSTGRES_USER=ricoh_admin
POSTGRES_PASSWORD=<pega-aquí-POSTGRES_PASSWORD>
POSTGRES_DB=ricoh_fleet
DATABASE_URL=postgresql://ricoh_admin:<pega-aquí-POSTGRES_PASSWORD>@postgres:5432/ricoh_fleet

# Redis
REDIS_PASSWORD=<pega-aquí-REDIS_PASSWORD>

# Security - Encryption & JWT
ENCRYPTION_KEY=<pega-aquí-ENCRYPTION_KEY>
SECRET_KEY=<pega-aquí-SECRET_KEY>

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS - Red local
CORS_ORIGINS=http://192.168.91.100,http://192.168.91.100:3000

# Ricoh Integration
RICOH_ADMIN_USERNAME=admin
RICOH_ADMIN_PASSWORD=<contraseña-admin-impresoras-ricoh>

# Frontend
FRONTEND_API_URL=http://192.168.91.100:8000

# Security
FORCE_HTTPS=false
CSRF_ENABLED=true
RATE_LIMIT_ENABLED=true
```

**Guardar el archivo:**
- Presiona `Ctrl+O` (guardar)
- Presiona `Enter` (confirmar nombre)
- Presiona `Ctrl+X` (salir)

---

## 💻 Fase 9: Desplegar la Aplicación (Desde tu PC via SSH)

```bash
cd /opt/ricoh

# Construir imágenes Docker
docker-compose -f deployment/docker-compose.prod.yml build

# Iniciar servicios
docker-compose -f deployment/docker-compose.prod.yml --env-file .env.production up -d

# Verificar estado
docker-compose -f deployment/docker-compose.prod.yml ps
```

**Deberías ver 5 contenedores corriendo:**
- ricoh-postgres
- ricoh-redis
- ricoh-backend
- ricoh-frontend
- ricoh-nginx

### 5.5 Verificar Logs

```bash
# Ver logs del backend
docker logs ricoh-backend

# Buscar mensajes de seguridad
docker logs ricoh-backend 2>&1 | grep -E "✅|🛡️|🔴"
```

**Deberías ver:**
```
✅ Servicio de encriptación inicializado
🛡️ CSRF Protection enabled
🔴 CSRF usando Redis para almacenamiento distribuido
🔴 Rate Limiter usando Redis para almacenamiento distribuido
```

---

## Fase 6: Inicializar Base de Datos

### 6.1 Ejecutar Migraciones

```bash
# Crear tablas de base de datos
docker exec ricoh-backend python scripts/init_db.py
```

### 6.2 Crear Usuario Superadmin

```bash
# Crear superadmin
docker exec ricoh-backend python scripts/init_superadmin.py

# Ver contraseña generada
docker exec ricoh-backend cat .superadmin_password
```

**IMPORTANTE**: Guarda esta contraseña. Usuario: `superadmin`

---

## Fase 7: Acceder a la Aplicación

### 7.1 Desde tu PC Windows

Abre tu navegador y accede a:

- **Frontend**: http://192.168.91.100
- **API Docs**: http://192.168.91.100:8000/docs
- **Health Check**: http://192.168.91.100:8000/health

### 7.2 Login Inicial

- **Usuario**: `superadmin`
- **Contraseña**: (la que obtuviste en el paso 6.2)

---

## Fase 8: Configuración para Servidor Rack 24/7

### 8.1 Deshabilitar Suspensión

```bash
# Deshabilitar todos los modos de suspensión
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# Verificar
sudo systemctl status sleep.target
```

### 8.2 Configurar Backups Automáticos

```bash
# Crear directorio de backups
sudo mkdir -p /opt/ricoh/backups

# Crear script de backup
sudo nano /opt/ricoh/backup.sh
```

**Contenido del script:**

```bash
#!/bin/bash
BACKUP_DIR="/opt/ricoh/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ricoh_backup_${TIMESTAMP}.sql"

# Crear backup
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > "$BACKUP_FILE"

# Comprimir
gzip "$BACKUP_FILE"

# Eliminar backups antiguos (mantener últimos 30 días)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup completado: ${BACKUP_FILE}.gz"
```

```bash
# Dar permisos de ejecución
sudo chmod +x /opt/ricoh/backup.sh

# Configurar cron para backups diarios a las 2 AM
sudo crontab -e

# Agregar esta línea:
0 2 * * * /opt/ricoh/backup.sh >> /opt/ricoh/backups/backup.log 2>&1
```

### 8.3 Configurar Monitoreo de Recursos

```bash
# Instalar herramientas de monitoreo
sudo apt install -y htop iotop lm-sensors

# Detectar sensores de temperatura
sudo sensors-detect --auto

# Ver temperaturas
sensors

# Ver uso de recursos
htop
```

### 8.4 Configurar Logs para No Llenar Disco

```bash
# Limitar tamaño de journal
sudo journalctl --vacuum-size=500M
sudo journalctl --vacuum-time=7d

# Configurar límite permanente
sudo nano /etc/systemd/journald.conf
```

Descomentar y configurar:
```
SystemMaxUse=500M
MaxRetentionSec=7day
```

```bash
# Reiniciar servicio
sudo systemctl restart systemd-journald
```

### 8.5 Configurar Servicio Systemd

```bash
# El script de setup ya creó el servicio, verificar:
sudo systemctl status ricoh.service

# Habilitar inicio automático
sudo systemctl enable ricoh.service

# Probar reinicio
sudo systemctl restart ricoh.service
```

---

## Fase 9: Seguridad Adicional

### 9.1 Configurar Fail2Ban (Protección SSH)

```bash
# Instalar Fail2Ban
sudo apt install -y fail2ban

# Crear configuración local
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Editar configuración
sudo nano /etc/fail2ban/jail.local
```

Buscar la sección `[sshd]` y asegurar:
```
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
```

```bash
# Habilitar y arrancar
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Verificar estado
sudo fail2ban-client status sshd
```

### 9.2 Deshabilitar Autenticación por Contraseña SSH (Opcional)

**Solo después de configurar claves SSH:**

```bash
# Editar configuración SSH
sudo nano /etc/ssh/sshd_config
```

Cambiar/agregar:
```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

```bash
# Reiniciar SSH
sudo systemctl restart sshd
```

---

## Comandos Útiles de Administración

### Gestión de Servicios Docker

```bash
# Ver estado de contenedores
docker-compose -f /opt/ricoh/deployment/docker-compose.prod.yml ps

# Ver logs en tiempo real
docker logs -f ricoh-backend

# Reiniciar servicios
docker-compose -f /opt/ricoh/deployment/docker-compose.prod.yml restart

# Detener servicios
docker-compose -f /opt/ricoh/deployment/docker-compose.prod.yml down

# Iniciar servicios
docker-compose -f /opt/ricoh/deployment/docker-compose.prod.yml up -d
```

### Monitoreo del Servidor

```bash
# Uso de recursos en tiempo real
docker stats

# Espacio en disco
df -h

# Uso de memoria
free -h

# Procesos activos
htop

# Temperatura del servidor
sensors

# Logs del sistema
sudo journalctl -f
```

### Actualización de la Aplicación

```bash
# Conectar al servidor
ssh ricoh-server

# Ir al directorio
cd /opt/ricoh

# Detener servicios
docker-compose -f deployment/docker-compose.prod.yml down

# Actualizar código
git pull origin main

# Reconstruir imágenes
docker-compose -f deployment/docker-compose.prod.yml build

# Iniciar servicios
docker-compose -f deployment/docker-compose.prod.yml up -d

# Verificar logs
docker logs -f ricoh-backend
```

---

## Checklist Final de Verificación

- [ ] Servidor rack con IP estática 192.168.91.100 configurada
- [ ] SSH funcionando desde tu PC (192.168.91.34)
- [ ] Autenticación por clave SSH configurada
- [ ] Docker y Docker Compose instalados
- [ ] Firewall UFW configurado (puertos 22, 80, 443)
- [ ] Aplicación desplegada y contenedores corriendo
- [ ] Base de datos inicializada
- [ ] Usuario superadmin creado
- [ ] Acceso web funcionando desde http://192.168.91.100
- [ ] Backups automáticos configurados (cron)
- [ ] Suspensión deshabilitada
- [ ] Logs configurados para no llenar disco
- [ ] Fail2Ban instalado y configurado
- [ ] Servicio systemd habilitado para inicio automático
- [ ] Todas las 11 correcciones de seguridad activas

---

## Troubleshooting Común

### No puedo conectar por SSH

```bash
# Desde el servidor (acceso físico)
sudo systemctl status ssh
sudo ufw status
sudo tail -f /var/log/auth.log

# Desde tu PC
ping 192.168.91.100
telnet 192.168.91.100 22
```

### Contenedores no inician

```bash
# Ver logs detallados
docker logs ricoh-backend
docker logs ricoh-postgres

# Verificar variables de entorno
docker exec ricoh-backend env | grep -E "ENCRYPTION|SECRET|DATABASE"

# Reiniciar servicios
docker-compose -f deployment/docker-compose.prod.yml restart
```

### No puedo acceder desde el navegador

```bash
# Verificar que nginx está corriendo
docker ps | grep nginx

# Verificar logs de nginx
docker logs ricoh-nginx

# Verificar firewall
sudo ufw status

# Probar desde el servidor
curl http://localhost
```

---

## Información de Contacto y Soporte

**Servidor**: 192.168.91.100  
**Administrador**: Juan Lizarazo  
**PC Admin**: TIC0264 (192.168.91.34)  
**Red**: RELITELTDA.LOCAL (192.168.91.0/24)  
**Gateway**: 192.168.91.1

**Documentación adicional**:
- `deployment/DEPLOYMENT_GUIDE.md` - Guía completa de deployment
- `deployment/SETUP_RACK_SERVER.md` - Configuración específica para rack
- `.kiro/specs/correccion-vulnerabilidades-seguridad-auditoria/` - Correcciones de seguridad

---

## Próximos Pasos (Opcional)

### Configurar Dominio Interno

Si quieres usar un nombre de dominio en lugar de la IP:

1. Configurar DNS interno en tu servidor DNS (11.0.20.10)
2. Agregar registro A: `ricoh.reliteltda.local → 192.168.91.100`
3. Actualizar CORS_ORIGINS en `.env.production`
4. Reiniciar servicios

### Configurar SSL/TLS

Para HTTPS en red local:

1. Generar certificado autofirmado o usar Let's Encrypt con dominio público
2. Copiar certificados a `deployment/ssl/`
3. Actualizar `FORCE_HTTPS=true` en `.env.production`
4. Reiniciar servicios

---

**Última actualización**: Marzo 2026  
**Versión**: 1.0
