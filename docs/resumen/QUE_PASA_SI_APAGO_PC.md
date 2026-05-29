# 💻 ¿Qué Pasa Si Apago Mi Computador?

**Fecha**: 6 de Mayo 2026  
**Configuración Actual**: Docker Local en PC  
**IP Local**: 192.168.91.34

---

## 🔴 Respuesta Corta

**Si apagas tu PC, TODO el sistema se cae.**

- ❌ Frontend: No accesible
- ❌ Backend: No accesible
- ❌ Base de datos: No accesible
- ❌ Redis: No accesible
- ❌ Usuarios: No pueden acceder al sistema

---

## 📊 Estado Actual del Sistema

### Configuración Actual

```
┌─────────────────────────────────────────┐
│         TU PC (192.168.91.34)           │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Docker Containers             │   │
│  │                                 │   │
│  │  • Frontend (Puerto 5173)       │   │
│  │  • Backend (Puerto 8000)        │   │
│  │  • PostgreSQL (Puerto 5432)     │   │
│  │  • Redis (Puerto 6379)          │   │
│  │  • Adminer (Puerto 8080)        │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
           │
           │ Red Local
           │
    ┌──────┴──────┐
    │             │
 Usuario A     Usuario B
 (Mismo WiFi)
```

### Acceso Actual

| Usuario | Ubicación | URL | Estado |
|---------|-----------|-----|--------|
| **Tú** | Tu PC | http://localhost:5173 | ✅ Funciona |
| **Otros** | Misma red WiFi | http://192.168.91.34:5173 | ✅ Funciona |
| **Otros** | Internet | ❌ No accesible | ❌ No funciona |

---

## ⚠️ Escenarios de Fallo

### Escenario 1: Apagas tu PC
```
PC Apagada → Docker se detiene → Todos los contenedores se detienen
```

**Resultado**:
- ❌ Frontend: Caído
- ❌ Backend: Caído
- ❌ Base de datos: Caída
- ❌ Redis: Caído
- ❌ **Usuarios no pueden acceder**

**Tiempo de recuperación**: Cuando enciendas tu PC y ejecutes `docker-compose up -d`

---

### Escenario 2: Tu PC se reinicia
```
PC Reiniciando → Docker se detiene → Contenedores se detienen
```

**Resultado**:
- ❌ Sistema caído durante reinicio (2-5 minutos)
- ⚠️ Contenedores NO se inician automáticamente
- ⚠️ Debes ejecutar `docker-compose up -d` manualmente

**Tiempo de recuperación**: 2-5 minutos + tiempo de iniciar Docker

---

### Escenario 3: Tu PC se suspende (Sleep)
```
PC en Sleep → Docker puede o no funcionar → Conexiones se pierden
```

**Resultado**:
- ⚠️ Conexiones de red se pierden
- ⚠️ Usuarios experimentan errores
- ⚠️ Sesiones pueden expirar

**Tiempo de recuperación**: Al despertar PC, puede requerir reiniciar contenedores

---

### Escenario 4: Se va la luz
```
Corte de luz → PC se apaga → Docker se detiene → Sistema caído
```

**Resultado**:
- ❌ Sistema completamente caído
- ⚠️ Riesgo de corrupción de base de datos
- ⚠️ Pérdida de datos en caché (Redis)

**Tiempo de recuperación**: Cuando vuelva la luz + encender PC + iniciar Docker

---

### Escenario 5: Falla tu WiFi
```
WiFi caído → PC sin red → Usuarios no pueden acceder
```

**Resultado**:
- ✅ Docker sigue corriendo
- ✅ Contenedores funcionando
- ❌ Usuarios no pueden acceder (sin red)

**Tiempo de recuperación**: Cuando se restaure WiFi

---

### Escenario 6: Cambias de red WiFi
```
Cambio de WiFi → IP cambia → URLs dejan de funcionar
```

**Resultado**:
- ⚠️ Tu IP cambia (ya no es 192.168.91.34)
- ❌ URLs antiguas no funcionan
- ⚠️ Debes actualizar VITE_API_URL en frontend

**Tiempo de recuperación**: Actualizar configuración y reiniciar frontend

---

## 🏢 Soluciones Disponibles

### Opción 1: Servidor Dedicado (RECOMENDADO)

**Descripción**: Contratar un servidor que esté siempre encendido

```
┌─────────────────────────────────────────┐
│    SERVIDOR EN LA NUBE (24/7)          │
│    (AWS, DigitalOcean, Azure, etc.)    │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Docker Containers             │   │
│  │                                 │   │
│  │  • Frontend                     │   │
│  │  • Backend                      │   │
│  │  • PostgreSQL                   │   │
│  │  • Redis                        │   │
│  │  • Nginx (HTTPS)                │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
           │
           │ Internet
           │
    ┌──────┴──────┐
    │             │
 Usuario A     Usuario B
 (Cualquier lugar del mundo)
```

**Ventajas**:
- ✅ Disponibilidad 24/7
- ✅ Acceso desde cualquier lugar
- ✅ HTTPS seguro
- ✅ Backups automáticos
- ✅ Escalable
- ✅ Profesional

**Desventajas**:
- 💰 Costo mensual ($5-50 USD/mes)
- 🔧 Requiere configuración inicial
- 📚 Requiere conocimientos de administración

**Costo Estimado**:
| Proveedor | Plan | Costo/Mes | Specs |
|-----------|------|-----------|-------|
| **DigitalOcean** | Droplet Básico | $6 USD | 1 CPU, 1GB RAM, 25GB SSD |
| **AWS Lightsail** | Básico | $5 USD | 1 CPU, 512MB RAM, 20GB SSD |
| **Linode** | Nanode | $5 USD | 1 CPU, 1GB RAM, 25GB SSD |
| **Vultr** | Cloud Compute | $6 USD | 1 CPU, 1GB RAM, 25GB SSD |
| **Hetzner** | CX11 | €4.15 EUR | 1 CPU, 2GB RAM, 20GB SSD |

**Recomendación**: DigitalOcean Droplet ($12/mes, 2GB RAM) para producción

---

### Opción 2: Servidor Local Dedicado

**Descripción**: Usar una PC vieja o Raspberry Pi como servidor

```
┌─────────────────────────────────────────┐
│    PC VIEJA / RASPBERRY PI (24/7)      │
│    (En tu oficina, siempre encendida)  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Docker Containers             │   │
│  │                                 │   │
│  │  • Frontend                     │   │
│  │  • Backend                      │   │
│  │  • PostgreSQL                   │   │
│  │  • Redis                        │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
           │
           │ Red Local
           │
    ┌──────┴──────┐
    │             │
 Usuario A     Usuario B
 (Misma red WiFi)
```

**Ventajas**:
- ✅ Sin costo mensual
- ✅ Control total
- ✅ Datos en tu red
- ✅ Disponible 24/7 (si no se apaga)

**Desventajas**:
- ❌ Solo accesible en red local
- ❌ Requiere PC siempre encendida
- ❌ Costo de electricidad
- ❌ Sin acceso desde internet
- ❌ Vulnerable a cortes de luz

**Costo Estimado**:
- PC vieja: $0 (si ya la tienes)
- Raspberry Pi 4: $50-100 USD (una vez)
- Electricidad: ~$5-10 USD/mes

---

### Opción 3: Mantener en Tu PC (ACTUAL)

**Descripción**: Seguir usando tu PC de trabajo

**Ventajas**:
- ✅ Gratis
- ✅ Fácil de desarrollar
- ✅ Control total

**Desventajas**:
- ❌ Sistema cae cuando apagas PC
- ❌ Solo red local
- ❌ No profesional
- ❌ No escalable
- ❌ Sin backups automáticos

**Recomendado para**:
- ✅ Desarrollo y pruebas
- ✅ Demos internos
- ❌ **NO para producción**

---

### Opción 4: Híbrido (Desarrollo + Producción)

**Descripción**: Mantener dos ambientes separados

```
DESARROLLO (Tu PC)          PRODUCCIÓN (Servidor)
┌─────────────────┐         ┌─────────────────┐
│  Docker Local   │         │  Docker Cloud   │
│                 │         │                 │
│  • Desarrollo   │         │  • Usuarios     │
│  • Pruebas      │  ───>   │  • 24/7         │
│  • Demos        │  Deploy │  • HTTPS        │
│                 │         │  • Backups      │
└─────────────────┘         └─────────────────┘
```

**Ventajas**:
- ✅ Mejor de ambos mundos
- ✅ Desarrollo local rápido
- ✅ Producción estable
- ✅ Profesional

**Desventajas**:
- 💰 Costo del servidor
- 🔧 Mantener dos ambientes

**Recomendado para**:
- ✅ **Proyectos serios**
- ✅ Equipos de desarrollo
- ✅ Producción real

---

## 🎯 Recomendación Según Caso de Uso

### Caso 1: Solo Desarrollo Personal
**Recomendación**: Mantener en tu PC (Opción 3)
```
✅ Gratis
✅ Suficiente para desarrollo
⚠️ No para usuarios reales
```

---

### Caso 2: Demo para Cliente
**Recomendación**: Servidor temporal (Opción 1)
```
✅ Profesional
✅ Accesible desde internet
✅ Puedes apagar tu PC
💰 $5-10 USD/mes
```

---

### Caso 3: Producción Real (Usuarios Reales)
**Recomendación**: Servidor dedicado + Backups (Opción 1)
```
✅ Disponibilidad 24/7
✅ HTTPS seguro
✅ Backups automáticos
✅ Escalable
💰 $12-50 USD/mes
```

---

### Caso 4: Oficina con Red Local
**Recomendación**: Servidor local dedicado (Opción 2)
```
✅ Sin costo mensual
✅ Datos en tu red
✅ Disponible 24/7
⚠️ Solo red local
💰 $50-100 USD (una vez)
```

---

## 🚀 Pasos para Migrar a Servidor

### Paso 1: Elegir Proveedor
Recomendado: **DigitalOcean** (fácil de usar)

1. Crear cuenta en https://www.digitalocean.com
2. Crear Droplet (servidor)
   - Ubuntu 22.04 LTS
   - 2GB RAM ($12/mes)
   - Región: New York o San Francisco

---

### Paso 2: Configurar Servidor

```bash
# Conectar por SSH
ssh root@tu-servidor-ip

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose-plugin -y

# Clonar tu proyecto
git clone https://github.com/tuempresa/ricoh-fleet.git
cd ricoh-fleet
```

---

### Paso 3: Configurar Producción

```bash
# Copiar configuración de producción
cp backend/.env.production.example backend/.env

# Editar con valores reales
nano backend/.env

# Generar claves de seguridad
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Actualizar .env con las claves
```

---

### Paso 4: Desplegar

```bash
# Iniciar servicios
docker-compose -f docker-compose.production.yml up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f

# Verificar estado
docker-compose -f docker-compose.production.yml ps
```

---

### Paso 5: Configurar Dominio (Opcional)

```bash
# Comprar dominio (ejemplo: ricoh.tuempresa.com)
# Apuntar DNS a IP del servidor

# Instalar Nginx y Certbot
apt install nginx certbot python3-certbot-nginx -y

# Obtener certificado SSL
certbot --nginx -d ricoh.tuempresa.com

# Configurar Nginx como reverse proxy
# Ver: docs/DEPLOYMENT_PRODUCTION.md
```

---

## 📊 Comparativa de Opciones

| Aspecto | Tu PC | PC Vieja | Servidor Cloud |
|---------|-------|----------|----------------|
| **Disponibilidad** | ❌ Solo cuando encendida | ⚠️ 24/7 (si no se apaga) | ✅ 24/7 garantizado |
| **Acceso** | ⚠️ Solo red local | ⚠️ Solo red local | ✅ Internet |
| **HTTPS** | ❌ HTTP | ❌ HTTP | ✅ HTTPS |
| **Backups** | ❌ Manual | ❌ Manual | ✅ Automático |
| **Costo** | ✅ Gratis | ⚠️ Electricidad | ⚠️ $5-50/mes |
| **Escalabilidad** | ❌ No | ❌ Limitada | ✅ Sí |
| **Profesional** | ❌ No | ⚠️ Limitado | ✅ Sí |
| **Mantenimiento** | ✅ Fácil | ⚠️ Medio | ⚠️ Medio |

---

## 💡 Consejos Prácticos

### Si Decides Mantener en Tu PC

1. **Configura Docker para iniciar automáticamente**
   ```bash
   # Windows: Docker Desktop → Settings → General
   # ✅ Start Docker Desktop when you log in
   ```

2. **Crea un script de inicio automático**
   ```bash
   # Crear archivo: startup.bat
   cd C:\Users\juan.lizarazo\Desktop\ricoh
   docker-compose up -d
   ```

3. **Configura tu PC para no suspenderse**
   ```
   Windows → Configuración → Sistema → Energía
   - Suspender: Nunca
   - Apagar pantalla: 30 minutos
   ```

4. **Documenta la IP actual**
   ```bash
   # Guardar IP en archivo
   ipconfig | Select-String -Pattern "IPv4" > ip_actual.txt
   ```

5. **Configura backups manuales**
   ```bash
   # Backup de base de datos
   docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > backup.sql
   ```

---

### Si Decides Migrar a Servidor

1. **Empieza con plan básico**
   - $5-12 USD/mes es suficiente para empezar
   - Puedes escalar después

2. **Usa la documentación completa**
   - `docs/DEPLOYMENT_PRODUCTION.md`
   - Guía paso a paso

3. **Prueba primero en servidor de prueba**
   - Crea servidor temporal
   - Prueba despliegue
   - Elimina si no funciona

4. **Configura backups desde el inicio**
   - Backups automáticos diarios
   - Retención de 30 días

5. **Monitorea el servidor**
   - Configura alertas
   - Revisa logs regularmente

---

## 🔧 Solución de Problemas

### Problema: Docker no inicia al encender PC

**Solución**:
```bash
# Windows: Configurar Docker Desktop
# Settings → General → Start Docker Desktop when you log in
```

---

### Problema: IP cambia constantemente

**Solución**:
```bash
# Opción A: Configurar IP estática en router
# Opción B: Usar servidor con IP fija
# Opción C: Usar dominio local (ricoh.local)
```

---

### Problema: Usuarios no pueden acceder

**Verificar**:
```bash
# 1. Docker corriendo
docker ps

# 2. Firewall permite conexiones
# Windows Firewall → Permitir aplicación

# 3. IP correcta
ipconfig | Select-String -Pattern "IPv4"

# 4. Usuarios en misma red WiFi
```

---

### Problema: Sistema lento en tu PC

**Solución**:
```bash
# Limitar recursos de Docker
# Docker Desktop → Settings → Resources
# - CPUs: 2
# - Memory: 4GB
# - Swap: 1GB
```

---

## 📞 Ayuda y Soporte

### Documentación
- **Despliegue Producción**: `docs/DEPLOYMENT_PRODUCTION.md`
- **Diferencias Local vs Producción**: `docs/DIFERENCIAS_LOCAL_VS_PRODUCCION.md`
- **Auditoría de Seguridad**: `docs/resumen/AUDITORIA_SEGURIDAD_6_MAYO_2026.md`

### Tutoriales Recomendados
- DigitalOcean: https://www.digitalocean.com/community/tutorials
- Docker: https://docs.docker.com/get-started/
- Nginx: https://nginx.org/en/docs/

---

## ✅ Resumen Final

### Tu Situación Actual
```
✅ Sistema funcionando en tu PC
✅ Accesible en red local (192.168.91.34)
✅ Correcto para DESARROLLO
❌ NO listo para PRODUCCIÓN
⚠️ Se cae si apagas tu PC
```

### Próximos Pasos Recomendados

**Corto Plazo (Ahora)**:
1. ✅ Mantener en tu PC para desarrollo
2. ✅ Documentar configuración actual
3. ✅ Hacer backups manuales de BD

**Mediano Plazo (1-2 semanas)**:
1. 🎯 Decidir si necesitas servidor
2. 🎯 Evaluar opciones y costos
3. 🎯 Planear migración

**Largo Plazo (1-2 meses)**:
1. 🚀 Migrar a servidor dedicado
2. 🚀 Configurar HTTPS
3. 🚀 Implementar backups automáticos
4. 🚀 Configurar monitoreo

---

**Última actualización**: 6 de Mayo 2026  
**Versión**: 1.0  
**Autor**: Equipo de Desarrollo Ricoh
