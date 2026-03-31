# Guía Simplificada - Servidor Rack RELITELTDA
## División Clara: Rack vs Tu PC

**Tu PC**: 192.168.91.34 (TIC0264) - SIN permisos de administrador  
**Servidor Rack**: 192.168.91.100 (a configurar)  
**Red**: 192.168.91.0/24 (RELITELTDA.LOCAL)

---

# 🏢 PARTE 1: EN EL RACK (Acceso Físico - Una Sola Vez)

## Qué necesitas en el rack:
- Monitor conectado al servidor
- Teclado USB conectado al servidor
- El servidor encendido con Ubuntu Server instalado

## Paso 1: Iniciar Sesión en el Servidor

```
Usuario: (el que creaste al instalar Ubuntu)
Contraseña: (la que configuraste)
```

## Paso 2: Identificar Interfaz de Red

```bash
ip a
```

Busca la interfaz activa (puede ser: `eth0`, `ens18`, `ens33`, `enp0s3`)  
**Anota el nombre**, lo necesitarás en el siguiente paso.

## Paso 3: Configurar IP Estática

```bash
sudo nano /etc/netplan/00-installer-config.yaml
```

**Reemplaza TODO el contenido con esto** (cambia `ens18` por tu interfaz):

```yaml
network:
  version: 2
  ethernets:
    ens18:  # CAMBIAR por tu interfaz del paso anterior
      addresses:
        - 192.168.91.100/24
      routes:
        - to: default
          via: 192.168.91.1
      nameservers:
        addresses:
          - 11.0.20.10
          - 8.8.8.8
```

**Guardar**: `Ctrl+O`, `Enter`, `Ctrl+X`

**Aplicar**:

```bash
sudo netplan apply
```

## Paso 4: Actualizar Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

## Paso 5: Instalar SSH

```bash
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

## Paso 6: Configurar Firewall

```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Cuando pregunte, escribe: `y` y presiona Enter

## Paso 7: Crear Usuario para Ti

```bash
sudo adduser ricoh-admin
```

Te pedirá:
- Nueva contraseña: **[elige una y guárdala]**
- Confirmar contraseña
- Información adicional: presiona Enter varias veces

```bash
sudo usermod -aG sudo ricoh-admin
```

## Paso 8: Verificar IP

```bash
ip a | grep "inet 192.168.91"
```

Deberías ver: `inet 192.168.91.100/24`

## Paso 9: Probar SSH

```bash
sudo systemctl status ssh
```

Deberías ver: `active (running)` en verde

## ✅ Listo en el Rack

**Anota esto antes de desconectar el monitor:**
- IP del servidor: **192.168.91.100**
- Usuario: **ricoh-admin**
- Contraseña: **[la que elegiste]**

**Ahora puedes:**
1. Cerrar sesión: `exit`
2. Desconectar el monitor
3. Desconectar el teclado
4. El servidor seguirá corriendo 24/7

---

# 💻 PARTE 2: DESDE TU PC (Todo lo Demás)

## Paso 1: Abrir PowerShell

1. Presiona `Windows + R`
2. Escribe: `powershell`
3. Presiona Enter

**No necesitas "Ejecutar como administrador"**

## Paso 2: Probar Conexión

```powershell
ping 192.168.91.100
```

Si ves respuestas, continúa. Si no, verifica que el servidor esté encendido.

## Paso 3: Conectar por SSH

```powershell
ssh ricoh-admin@192.168.91.100
```

- Te preguntará: `Are you sure...?` → Escribe: `yes` → Enter
- Te pedirá la contraseña → Escríbela (no se ve) → Enter

**¡Conectado!** Ahora estás dentro del servidor desde tu PC.

## Paso 4: Generar Clave SSH (Para No Escribir Contraseña)

**Abre OTRA ventana de PowerShell** (deja la anterior abierta):

```powershell
ssh-keygen -t ed25519 -C "juan.lizarazo@reliteltda.local"
```

- `Enter file...`: Presiona Enter
- `Enter passphrase`: Presiona Enter (sin contraseña)
- `Enter same passphrase`: Presiona Enter

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh ricoh-admin@192.168.91.100 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Te pedirá la contraseña una última vez.

**Probar**:

```powershell
ssh ricoh-admin@192.168.91.100
```

Ahora debería conectar SIN pedir contraseña.

## Paso 5: Crear Alias (Opcional pero Útil)

```powershell
notepad $env:USERPROFILE\.ssh\config
```

Si dice que no existe, acepta crearlo.

**Pega esto:**

```
Host ricoh-server
    HostName 192.168.91.100
    User ricoh-admin
    IdentityFile ~/.ssh/id_ed25519
```

Guarda (`Ctrl+S`) y cierra.

**Ahora puedes conectar con:**

```powershell
ssh ricoh-server
```

## Paso 6: Copiar Script de Setup al Servidor

**Desde PowerShell en tu PC** (en el directorio del proyecto):

```powershell
cd C:\ruta\a\tu\proyecto

scp deployment/setup-ubuntu-server.sh ricoh-admin@192.168.91.100:~/
```

## Paso 7: Ejecutar Script de Setup

**Conectar al servidor:**

```powershell
ssh ricoh-server
```

**En el servidor:**

```bash
chmod +x setup-ubuntu-server.sh
sudo bash setup-ubuntu-server.sh
```

**Espera 5-10 minutos**. Verás mensajes en verde (✓) cuando termine cada paso.

## Paso 8: Preparar Directorio de Aplicación

```bash
sudo mkdir -p /opt/ricoh
sudo chown -R ricoh:ricoh /opt/ricoh
```

## Paso 9: Copiar Código al Servidor

**Opción A: Si tienes Git en el servidor**

```bash
cd /opt/ricoh
sudo git clone https://github.com/tu-org/ricoh-equipment-management.git .
sudo chown -R ricoh:ricoh /opt/ricoh
```

**Opción B: Copiar desde tu PC**

Abre OTRA ventana de PowerShell en tu PC:

```powershell
cd C:\ruta\a\tu\proyecto

scp -r backend ricoh-admin@192.168.91.100:/opt/ricoh/
scp -r frontend ricoh-admin@192.168.91.100:/opt/ricoh/
scp -r deployment ricoh-admin@192.168.91.100:/opt/ricoh/
```

## Paso 10: Generar Claves de Seguridad

**En el servidor (via SSH):**

```bash
cd /opt/ricoh

python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

**Copia el resultado** y pégalo en un archivo de texto en tu PC.

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

**Copia el resultado** y pégalo en tu archivo de texto.

```bash
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24))"
```

**Copia el resultado** y pégalo en tu archivo de texto.

```bash
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(24))"
```

**Copia el resultado** y pégalo en tu archivo de texto.

**Guarda este archivo en un lugar seguro.**

## Paso 11: Configurar Variables de Entorno

```bash
cd /opt/ricoh
cp deployment/.env.production.example .env.production
nano .env.production
```

**Busca y reemplaza estas líneas** (usa las claves que generaste):

```bash
POSTGRES_PASSWORD=<pega-aquí-POSTGRES_PASSWORD>
DATABASE_URL=postgresql://ricoh_admin:<pega-aquí-POSTGRES_PASSWORD>@postgres:5432/ricoh_fleet

REDIS_PASSWORD=<pega-aquí-REDIS_PASSWORD>

ENCRYPTION_KEY=<pega-aquí-ENCRYPTION_KEY>
SECRET_KEY=<pega-aquí-SECRET_KEY>

CORS_ORIGINS=http://192.168.91.100,http://192.168.91.100:3000

RICOH_ADMIN_PASSWORD=<contraseña-admin-impresoras-ricoh>

FRONTEND_API_URL=http://192.168.91.100:8000

FORCE_HTTPS=false
```

**Guardar**: `Ctrl+O`, Enter, `Ctrl+X`

## Paso 12: Construir y Desplegar

```bash
cd /opt/ricoh

sudo docker-compose -f deployment/docker-compose.prod.yml build
```

**Espera 5-10 minutos** (primera vez tarda más).

```bash
sudo docker-compose -f deployment/docker-compose.prod.yml --env-file .env.production up -d
```

**Verificar:**

```bash
sudo docker-compose -f deployment/docker-compose.prod.yml ps
```

Deberías ver 5 contenedores con estado "Up".

## Paso 13: Inicializar Base de Datos

```bash
sudo docker exec ricoh-backend python scripts/init_db.py
```

```bash
sudo docker exec ricoh-backend python scripts/init_superadmin.py
```

```bash
sudo docker exec ricoh-backend cat .superadmin_password
```

**Copia esta contraseña** y guárdala. Usuario: `superadmin`

## Paso 14: Acceder desde tu Navegador

Abre tu navegador en tu PC y ve a:

- **http://192.168.91.100**

Login:
- Usuario: `superadmin`
- Contraseña: (la que copiaste en el paso 13)

**¡Listo! La aplicación está funcionando.**

---

# 📋 COMANDOS ÚTILES DESDE TU PC

## Conectar al Servidor

```powershell
ssh ricoh-server
```

## Ver Estado de Servicios

```bash
sudo docker-compose -f /opt/ricoh/deployment/docker-compose.prod.yml ps
```

## Ver Logs

```bash
sudo docker logs -f ricoh-backend
```

Salir de logs: `Ctrl+C`

## Reiniciar Servicios

```bash
cd /opt/ricoh
sudo docker-compose -f deployment/docker-compose.prod.yml restart
```

## Ver Uso de Recursos

```bash
sudo docker stats
```

Salir: `Ctrl+C`

## Copiar Archivo de tu PC al Servidor

```powershell
scp C:\ruta\al\archivo.txt ricoh-admin@192.168.91.100:/opt/ricoh/
```

## Copiar Archivo del Servidor a tu PC

```powershell
scp ricoh-admin@192.168.91.100:/opt/ricoh/archivo.txt C:\Users\juan.lizarazo\Desktop\
```

---

# 🆘 TROUBLESHOOTING

## No puedo conectar por SSH

```powershell
# Desde tu PC
ping 192.168.91.100
```

Si no responde:
- Verifica que el servidor esté encendido
- Ve físicamente al rack y verifica que el cable de red esté conectado

## Olvidé la contraseña del servidor

Necesitas acceso físico al rack para resetearla desde el modo recovery de Ubuntu.

## Los contenedores no inician

```bash
ssh ricoh-server
sudo docker logs ricoh-backend
```

Busca errores en rojo.

## No puedo acceder desde el navegador

```bash
ssh ricoh-server
sudo docker ps
```

Verifica que todos los contenedores estén "Up".

```bash
sudo ufw status
```

Verifica que el puerto 80 esté permitido.

---

# ✅ CHECKLIST FINAL

## En el Rack (Una sola vez):
- [ ] IP estática configurada (192.168.91.100)
- [ ] SSH instalado y corriendo
- [ ] Firewall configurado
- [ ] Usuario ricoh-admin creado
- [ ] Monitor y teclado desconectados

## Desde tu PC:
- [ ] Puedes conectar por SSH sin contraseña
- [ ] Script de setup ejecutado
- [ ] Código copiado al servidor
- [ ] Variables de entorno configuradas
- [ ] Servicios Docker corriendo
- [ ] Base de datos inicializada
- [ ] Puedes acceder desde el navegador

---

**Servidor**: 192.168.91.100  
**Tu PC**: 192.168.91.34 (TIC0264)  
**Usuario SSH**: ricoh-admin  
**Usuario App**: superadmin

