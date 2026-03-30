# Setup para PC Rack 24/7 con Dominio

Instrucciones específicas para desplegar en un servidor rack 24/7.

## Requisitos del Servidor Rack

- **OS**: Ubuntu Server 22.04/24.04 LTS
- **RAM**: Mínimo 8GB (recomendado 16GB)
- **CPU**: Mínimo 4 cores
- **Disco**: SSD 50GB+ (recomendado 100GB)
- **Red**: IP estática + dominio configurado
- **UPS**: Recomendado para protección de datos

## Configuración de Red

### 1. IP Estática

Editar `/etc/netplan/00-installer-config.yaml`:

```yaml
network:
  version: 2
  ethernets:
    ens18:  # Ajustar nombre de interfaz
      addresses:
        - 192.168.1.100/24  # Tu IP estática
      routes:
        - to: default
          via: 192.168.1.1  # Tu gateway
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Aplicar:
```bash
sudo netplan apply
```

### 2. Configurar Dominio

En tu proveedor de DNS (Cloudflare, GoDaddy, etc.):

```
A     ricoh.tu-dominio.com      →  IP-DEL-SERVIDOR
A     api.ricoh.tu-dominio.com  →  IP-DEL-SERVIDOR
```

## Instalación Paso a Paso

### 1. Conectar al Servidor

```bash
ssh usuario@IP-DEL-SERVIDOR
```

### 2. Ejecutar Setup Automático

```bash
# Descargar script
wget https://raw.githubusercontent.com/tu-repo/main/deployment/setup-ubuntu-server.sh

# Ejecutar
sudo bash setup-ubuntu-server.sh
```

### 3. Clonar Repositorio

```bash
cd /opt/ricoh
sudo git clone https://github.com/tu-org/ricoh.git .
sudo chown -R ricoh:ricoh /opt/ricoh
```

### 4. Configurar Variables

```bash
cp deployment/.env.production.example .env.production
nano .env.production
```

Configurar:
- ENCRYPTION_KEY (generar nueva)
- SECRET_KEY (generar nueva)
- POSTGRES_PASSWORD (generar nueva)
- REDIS_PASSWORD (generar nueva)
- RICOH_ADMIN_PASSWORD (tu contraseña de impresoras)
- CORS_ORIGINS=https://ricoh.tu-dominio.com
- DOMAIN_NAME=ricoh.tu-dominio.com
- API_DOMAIN=api.ricoh.tu-dominio.com

### 5. SSL Certificates

```bash
sudo certbot certonly --standalone \
  -d ricoh.tu-dominio.com \
  -d api.ricoh.tu-dominio.com \
  --email tu-email@dominio.com

sudo mkdir -p /opt/ricoh/deployment/ssl
sudo cp /etc/letsencrypt/live/ricoh.tu-dominio.com/fullchain.pem /opt/ricoh/deployment/ssl/
sudo cp /etc/letsencrypt/live/ricoh.tu-dominio.com/privkey.pem /opt/ricoh/deployment/ssl/
sudo chown ricoh:ricoh /opt/ricoh/deployment/ssl/*
```

### 6. Actualizar Nginx Config

```bash
nano deployment/nginx/conf.d/ricoh.conf
```

Reemplazar todas las ocurrencias de:
- `${DOMAIN_NAME}` → `ricoh.tu-dominio.com`
- `${API_DOMAIN}` → `api.ricoh.tu-dominio.com`

### 7. Deploy

```bash
su - ricoh
cd /opt/ricoh
bash deployment/deploy-production.sh
```

### 8. Inicializar

```bash
docker exec ricoh-backend python scripts/init_db.py
docker exec ricoh-backend python scripts/init_superadmin.py
docker exec ricoh-backend cat .superadmin_password
```

### 9. Verificar

```bash
docker exec ricoh-backend python scripts/verify_deployment.py
bash deployment/verify-security-fixes.sh
```

## Acceso al Sistema

- **Frontend**: https://ricoh.tu-dominio.com
- **API**: https://api.ricoh.tu-dominio.com
- **Adminer**: http://IP-SERVIDOR:8080 (solo red local)

## Mantenimiento del Servidor Rack

### Backups Automáticos

Ya configurados en crontab (diario a las 2 AM):
```bash
crontab -l  # Ver backups configurados
```

### Monitoreo

```bash
# Estado de servicios
docker-compose -f deployment/docker-compose.prod.yml ps

# Uso de recursos
docker stats

# Logs
docker logs -f ricoh-backend
```

### Actualizaciones

```bash
cd /opt/ricoh
git pull
bash deployment/deploy-production.sh
```

## Consideraciones para Rack 24/7

1. **UPS**: Configurar apagado automático
2. **Monitoreo**: Considerar Prometheus + Grafana
3. **Alertas**: Configurar notificaciones por email/SMS
4. **Backups**: Verificar que se ejecutan diariamente
5. **Logs**: Revisar semanalmente

## Troubleshooting Común

Ver `deployment/DEPLOYMENT_GUIDE.md` sección Troubleshooting.


---

## Configuración Específica para Servidor Rack

### Hardware Monitoring

Instalar herramientas de monitoreo:

```bash
sudo apt-get install -y lm-sensors smartmontools

# Detectar sensores
sudo sensors-detect --auto

# Ver temperaturas
sensors

# Ver estado de discos
sudo smartctl -a /dev/sda
```

### Configurar Alertas de Temperatura

```bash
# Instalar hddtemp
sudo apt-get install -y hddtemp

# Agregar a crontab (cada hora)
crontab -e

# Agregar:
0 * * * * sensors | grep -i "temp" | mail -s "Server Temperature" tu-email@dominio.com
```

### UPS Configuration (si tienes UPS)

```bash
# Instalar NUT (Network UPS Tools)
sudo apt-get install -y nut

# Configurar en /etc/nut/ups.conf
# Ver documentación de tu UPS específico
```

### Monitoreo de Recursos

```bash
# Instalar htop y iotop
sudo apt-get install -y htop iotop

# Ver uso en tiempo real
htop
iotop
```

---

## Optimizaciones para 24/7

### 1. Deshabilitar Suspensión

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### 2. Configurar Logs para No Llenar Disco

```bash
# Limitar tamaño de journal
sudo journalctl --vacuum-size=500M
sudo journalctl --vacuum-time=7d

# Configurar límite permanente
sudo nano /etc/systemd/journald.conf
# Descomentar y configurar:
# SystemMaxUse=500M
# MaxRetentionSec=7day
```

### 3. Monitoreo de Disco

```bash
# Agregar a crontab (diario)
0 6 * * * df -h | grep -E "/$|/opt" | awk '{if ($5+0 > 80) print "Disk usage high: " $0}' | mail -s "Disk Alert" tu-email@dominio.com
```

---

## Acceso Remoto Seguro

### SSH Key-Based Authentication

```bash
# En tu máquina local, generar key
ssh-keygen -t ed25519 -C "tu-email@dominio.com"

# Copiar al servidor
ssh-copy-id usuario@IP-SERVIDOR

# En el servidor, deshabilitar password auth
sudo nano /etc/ssh/sshd_config
# Configurar:
# PasswordAuthentication no
# PubkeyAuthentication yes

sudo systemctl restart sshd
```

### Fail2Ban (protección contra brute force)

```bash
sudo apt-get install -y fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Habilitar protección SSH
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Checklist Final para Rack Server

- [ ] IP estática configurada
- [ ] Dominio apuntando al servidor
- [ ] SSL certificates instalados
- [ ] Firewall configurado (UFW)
- [ ] SSH key-based auth configurado
- [ ] Fail2Ban instalado
- [ ] Suspensión deshabilitada
- [ ] Monitoreo de temperatura configurado
- [ ] Backups automáticos configurados
- [ ] Log rotation configurado
- [ ] UPS configurado (si aplica)
- [ ] Aplicación desplegada y verificada
- [ ] Todas las 11 correcciones de seguridad activas

---

## Contacto de Emergencia

Documentar información de contacto:

- **Administrador del Sistema**: _______________
- **Teléfono**: _______________
- **Email**: _______________
- **Proveedor de Internet**: _______________
- **Proveedor de Dominio**: _______________
- **Ubicación Física del Servidor**: _______________
