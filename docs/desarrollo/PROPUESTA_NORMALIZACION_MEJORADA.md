# Propuesta de Normalización Mejorada con Sincronización Automática

## 📊 Resumen Ejecutivo

### Situación Actual
- **6 usuarios** registrados manualmente en `users`
- **435 usuarios únicos** detectados en lecturas de contadores desde equipos
- **429 usuarios activos** (últimos 30 días) sin registro en `users`
- **21,356 registros** en `contadores_usuario` con datos redundantes
- **6,776 registros** en `cierres_mensuales_usuarios` con datos redundantes

### Problema Principal
Cuando se leen contadores desde las impresoras, los usuarios detectados NO se guardan en la tabla `users`. Solo se guardaban cuando se modificaban permisos manualmente en "Gestión de Usuarios". Esto genera:
- 429 usuarios "huérfanos" sin FK
- Datos duplicados (codigo_usuario + nombre_usuario como texto)
- Imposibilidad de gestionar permisos centralizadamente
- Queries lentas (comparación de strings vs integers)

### Solución Propuesta
**Sincronización automática de usuarios al leer contadores:**
1. **Primera vez**: Crea masivamente los 429 usuarios faltantes
2. **Lecturas posteriores**: Solo crea usuarios nuevos cuando aparecen en equipos
3. **Sin intervención manual**: Los usuarios se crean automáticamente
4. **Gestión centralizada**: Todos los usuarios visibles en tabla `users`
5. **Normalización**: Usar `user_id` (FK) en lugar de texto

### Beneficios Inmediatos
- ✓ 429 usuarios sincronizados automáticamente
- ✓ Gestión de permisos centralizada
- ✓ Queries 2-3x más rápidas (JOIN por integer vs string)
- ✓ Visibilidad completa: usuarios por impresora
- ✓ Reportes más precisos y eficientes
- ✓ Escalabilidad para crecimiento futuro

### Impacto
- **Tiempo de implementación**: 2-4 semanas
- **Downtime**: Ventana de mantenimiento de 5-10 minutos
- **Riesgo**: Bajo (se mantienen campos antiguos para compatibilidad)
- **ROI**: Alto (mejora inmediata en gestión y performance)

---

## 📋 Contexto del Problema

### Situación Actual
- **6 usuarios** registrados manualmente en `users`
- **435 usuarios únicos** detectados en lecturas de contadores desde equipos
- **429 usuarios activos** sin registro en `users` (huérfanos)
- **19,833 registros** en `contadores_usuario` con datos redundantes (codigo_usuario, nombre_usuario)
- **6,776 registros** en `cierres_mensuales_usuarios` con los mismos datos redundantes

### Flujo Actual (Ineficiente)
```
1. Lectura de contadores desde impresora
   ↓
2. Se guarda: codigo_usuario + nombre_usuario (texto) en contadores_usuario
   ↓
3. Usuario NO se crea en tabla users
   ↓
4. Solo se guardaba en users cuando se modificaban permisos manualmente
   ↓
5. Al hacer cierre mensual: se copian codigo_usuario + nombre_usuario (redundancia)
   ↓
6. Resultado: 429 usuarios activos sin registro en users, datos duplicados
```

---

## ✅ Propuesta: Normalización + Sincronización Automática

### Flujo Mejorado (Con Sincronización Automática)
```
1. Lectura de contadores desde impresora
   ↓
2. Por cada usuario detectado en el equipo:
   - ¿Existe en users con ese codigo_de_usuario?
     → SÍ: Usar user_id existente
     → NO: Crear automáticamente en users con datos básicos
   ↓
3. Guardar en contadores_usuario:
   - user_id (FK) ← NUEVO (normalizado)
   - codigo_usuario (mantener para compatibilidad)
   - nombre_usuario (mantener para compatibilidad)
   ↓
4. Al hacer cierre mensual:
   - Usar user_id directamente (FK normalizada)
   - Mantener codigo_usuario/nombre_usuario para históricos
   ↓
5. Resultado: 
   - Primera vez: Crea masivamente los 429 usuarios faltantes
   - Lecturas posteriores: Solo crea usuarios nuevos detectados
   - Todos los usuarios normalizados, sin huérfanos
   - Gestión de permisos centralizada en tabla users
```

---

## 🎯 Beneficios de la Propuesta

### 1. Sincronización Automática
- **Primera vez**: Crea masivamente los 429 usuarios faltantes detectados en equipos
- **Lecturas posteriores**: Solo crea usuarios nuevos cuando aparecen en los equipos
- **Sin intervención manual**: Los usuarios se crean automáticamente al leer contadores
- **Gestión de permisos**: Se puede modificar permisos posteriormente en la tabla users centralizada
- **Visibilidad completa**: Todos los usuarios del sistema visibles en un solo lugar

### 2. Integridad Referencial
- Todos los contadores apuntan a `users.id` válido
- Queries más rápidas (JOIN por entero vs string)
- Cascadas y validaciones automáticas

### 3. Gestión Centralizada
- Un solo lugar para ver todos los usuarios del sistema
- Fácil identificar usuarios activos vs inactivos
- Reportes y estadísticas más precisos

### 4. Compatibilidad Histórica
- Se mantienen `codigo_usuario` y `nombre_usuario` para registros antiguos
- No se rompe código existente que consulte por estos campos
- Migración gradual: nuevos registros usan user_id, antiguos mantienen ambos
- Reportes históricos siguen funcionando sin cambios

---

## 📐 Diseño de la Solución

### Fase 1: Agregar Columnas FK

```sql
-- Agregar user_id a contadores_usuario
ALTER TABLE contadores_usuario 
ADD COLUMN user_id INTEGER;

-- Agregar user_id a cierres_mensuales_usuarios
ALTER TABLE cierres_mensuales_usuarios 
ADD COLUMN user_id INTEGER;

-- Índices para performance
CREATE INDEX idx_contadores_usuario_user_id ON contadores_usuario(user_id);
CREATE INDEX idx_cierres_usuarios_user_id ON cierres_mensuales_usuarios(user_id);
```

### Fase 2: Sincronización Masiva Inicial

```sql
-- Crear usuarios faltantes automáticamente (429 usuarios activos)
-- Solo usuarios con actividad reciente (últimos 30 días)
INSERT INTO users (
    name,
    codigo_de_usuario,
    network_username,
    network_password_encrypted,
    smb_server,
    smb_port,
    smb_path,
    func_copier,
    func_printer,
    func_scanner,
    is_active,
    created_at
)
SELECT DISTINCT
    cu.nombre_usuario,
    cu.codigo_usuario,
    'reliteltda\\scaner',  -- Valor por defecto del sistema
    '',  -- Sin password inicialmente (se configura después si es necesario)
    '192.168.91.5',  -- Servidor SMB por defecto
    21,  -- Puerto por defecto
    '\\\\servidor\\Escaner',  -- Path genérico (se personaliza después)
    false,  -- Permisos deshabilitados por defecto
    false,  -- Se habilitan manualmente según necesidad
    false,
    true,  -- Usuario activo (detectado en equipos)
    NOW()
FROM contadores_usuario cu
WHERE NOT EXISTS (
    SELECT 1 FROM users u 
    WHERE u.codigo_de_usuario = cu.codigo_usuario
)
AND cu.fecha_lectura >= NOW() - INTERVAL '30 days'  -- Solo usuarios activos recientes
ORDER BY cu.codigo_usuario;

-- Resultado esperado: ~429 usuarios creados
```

### Fase 3: Poblar user_id en Registros Existentes

```sql
-- Actualizar contadores_usuario
UPDATE contadores_usuario cu
SET user_id = u.id
FROM users u
WHERE u.codigo_de_usuario = cu.codigo_usuario;

-- Actualizar cierres_mensuales_usuarios
UPDATE cierres_mensuales_usuarios cmu
SET user_id = u.id
FROM users u
WHERE u.codigo_de_usuario = cmu.codigo_usuario;
```

### Fase 4: Agregar FK Constraints

```sql
-- FK para contadores_usuario
ALTER TABLE contadores_usuario
ADD CONSTRAINT fk_contadores_usuario_user_id 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE SET NULL;

-- FK para cierres_mensuales_usuarios
ALTER TABLE cierres_mensuales_usuarios
ADD CONSTRAINT fk_cierres_usuarios_user_id 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE SET NULL;
```

---

## 💻 Cambios en el Código Backend

### 1. Servicio de Sincronización de Usuarios

```python
# backend/services/user_sync_service.py

from sqlalchemy.orm import Session
from backend.db.models import User
from backend.logger import logger

class UserSyncService:
    """
    Servicio para sincronizar usuarios detectados en equipos
    con la tabla users.
    
    Este servicio implementa la sincronización automática:
    - Primera vez: Crea masivamente usuarios faltantes
    - Lecturas posteriores: Solo crea usuarios nuevos
    """
    
    @staticmethod
    def sync_user_from_counter(
        codigo_usuario: str,
        nombre_usuario: str,
        db: Session,
        printer_id: int = None
    ) -> int:
        """
        Sincroniza un usuario detectado en contador.
        Si no existe, lo crea automáticamente con permisos deshabilitados.
        
        Args:
            codigo_usuario: Código único del usuario (8 dígitos)
            nombre_usuario: Nombre completo del usuario
            db: Sesión de base de datos
            printer_id: ID de la impresora donde se detectó (opcional, para logging)
        
        Returns:
            user_id del usuario (existente o recién creado)
        """
        # Buscar usuario existente por código
        user = db.query(User).filter(
            User.codigo_de_usuario == codigo_usuario
        ).first()
        
        if user:
            # Usuario ya existe, retornar su ID
            return user.id
        
        # Usuario no existe, crear automáticamente
        new_user = User(
            name=nombre_usuario,
            codigo_de_usuario=codigo_usuario,
            network_username="reliteltda\\scaner",  # Valor por defecto del sistema
            network_password_encrypted="",  # Sin password inicial
            smb_server="192.168.91.5",  # Servidor SMB por defecto
            smb_port=21,
            smb_path=f"\\\\servidor\\{nombre_usuario}",  # Path personalizado
            func_copier=False,  # Permisos deshabilitados por defecto
            func_printer=False,  # Se habilitan manualmente según necesidad
            func_scanner=False,
            is_active=True  # Usuario activo (detectado en equipo)
        )
        
        db.add(new_user)
        db.flush()  # Para obtener el ID sin hacer commit
        
        printer_info = f" en impresora {printer_id}" if printer_id else ""
        logger.info(
            f"✓ Usuario auto-creado{printer_info}: "
            f"{codigo_usuario} - {nombre_usuario} (ID: {new_user.id})"
        )
        
        return new_user.id
    
    @staticmethod
    def sync_all_users_from_counters(db: Session, days: int = 30) -> dict:
        """
        Sincronización masiva de todos los usuarios detectados en contadores.
        Útil para la migración inicial.
        
        Args:
            db: Sesión de base de datos
            days: Días hacia atrás para considerar usuarios activos
        
        Returns:
            dict con estadísticas: {created: int, existing: int, total: int}
        """
        from backend.db.models import ContadorUsuario
        from datetime import datetime, timedelta
        
        # Obtener usuarios únicos de contadores (últimos N días)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        usuarios_detectados = db.query(
            ContadorUsuario.codigo_usuario,
            ContadorUsuario.nombre_usuario
        ).filter(
            ContadorUsuario.fecha_lectura >= cutoff_date
        ).distinct().all()
        
        created = 0
        existing = 0
        
        for codigo, nombre in usuarios_detectados:
            # Verificar si existe
            user = db.query(User).filter(
                User.codigo_de_usuario == codigo
            ).first()
            
            if user:
                existing += 1
            else:
                # Crear usuario
                new_user = User(
                    name=nombre,
                    codigo_de_usuario=codigo,
                    network_username="reliteltda\\scaner",
                    network_password_encrypted="",
                    smb_server="192.168.91.5",
                    smb_port=21,
                    smb_path=f"\\\\servidor\\{nombre}",
                    func_copier=False,
                    func_printer=False,
                    func_scanner=False,
                    is_active=True
                )
                db.add(new_user)
                created += 1
        
        db.commit()
        
        logger.info(
            f"Sincronización masiva completada: "
            f"{created} usuarios creados, {existing} ya existían"
        )
        
        return {
            "created": created,
            "existing": existing,
            "total": created + existing
        }
```

### 2. Modificar Guardado de Contadores (Sincronización Automática)

```python
# backend/services/counter_service.py

from backend.services.user_sync_service import UserSyncService

def save_user_counter(
    printer_id: int,
    codigo_usuario: str,
    nombre_usuario: str,
    counter_data: dict,
    db: Session
):
    """
    Guarda contador de usuario con sincronización automática.
    
    CAMBIO CLAVE: Ahora sincroniza automáticamente el usuario
    en la tabla users si no existe.
    """
    # ✓ NUEVO: Sincronizar usuario automáticamente
    # Primera vez: Crea el usuario si no existe
    # Lecturas posteriores: Usa el user_id existente
    user_id = UserSyncService.sync_user_from_counter(
        codigo_usuario=codigo_usuario,
        nombre_usuario=nombre_usuario,
        printer_id=printer_id,
        db=db
    )
    
    # Crear registro de contador con FK normalizada
    contador = ContadorUsuario(
        printer_id=printer_id,
        user_id=user_id,  # ← NUEVO: FK normalizada a users
        codigo_usuario=codigo_usuario,  # Mantener para compatibilidad
        nombre_usuario=nombre_usuario,  # Mantener para compatibilidad
        total_paginas=counter_data.get('total_paginas', 0),
        total_impresiones=counter_data.get('total_impresiones', 0),
        total_copias=counter_data.get('total_copias', 0),
        # ... resto de campos
    )
    
    db.add(contador)
    db.commit()
    
    return contador
```

### 3. Modificar Creación de Cierres

```python
# backend/services/cierre_service.py

def create_cierre_mensual(
    printer_id: int,
    periodo_inicio: date,
    periodo_fin: date,
    db: Session
):
    """
    Crea cierre mensual con user_id normalizado
    """
    # ... crear cierre principal ...
    
    # Obtener últimos contadores por usuario
    contadores = db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.fecha_lectura.between(periodo_inicio, periodo_fin)
    ).all()
    
    for contador in contadores:
        cierre_usuario = CierreMensualUsuario(
            cierre_mensual_id=cierre.id,
            user_id=contador.user_id,  # ← NUEVO: FK normalizada
            codigo_usuario=contador.codigo_usuario,  # Mantener para históricos
            nombre_usuario=contador.nombre_usuario,  # Mantener para históricos
            total_paginas=contador.total_paginas,
            # ... resto de campos
        )
        db.add(cierre_usuario)
    
    db.commit()
```

---

## 🔄 Estrategia de Migración

### Paso 1: Preparación (Sin Downtime)
```bash
# Ejecutar migración 012 (agregar columnas, índices)
psql -U ricoh_admin -d ricoh_fleet < backend/migrations/012_normalize_user_references.sql
```

### Paso 2: Sincronización Masiva (Mantenimiento)
```bash
# Crear usuarios faltantes (429 usuarios)
# Poblar user_id en registros existentes (26,609 registros)
# Tiempo estimado: 2-5 minutos
```

### Paso 3: Desplegar Código Nuevo
```bash
# Actualizar backend con UserSyncService
# El código nuevo usa user_id
# El código viejo sigue funcionando (campos antiguos se mantienen)
```

### Paso 4: Monitoreo
```sql
-- Verificar que no haya usuarios huérfanos
SELECT COUNT(*) 
FROM contadores_usuario 
WHERE user_id IS NULL;

-- Debe ser 0 para usuarios activos recientes
```

---

## 📊 Impacto Esperado

### Performance
- **Queries 2-3x más rápidas** (JOIN por integer vs string)
- **Índices más pequeños** (4 bytes vs 8-100 bytes)
- **Menos I/O** en disco

### Espacio en Disco
- **Ahorro inmediato:** ~374 KB
- **Ahorro proyectado (1 año):** ~4.5 MB
- **Beneficio real:** Escalabilidad para crecimiento

### Mantenibilidad
- **Un solo lugar** para gestionar usuarios
- **Reportes más fáciles** (usuarios activos, inactivos, por impresora)
- **Auditoría mejorada** (quién hizo qué, cuándo)

---

## 🎓 Casos de Uso Mejorados

### Caso 1: Lectura Automática de Contadores (Sincronización Automática)
```python
# ANTES: Solo guardaba texto, usuario no se creaba en users
contador = ContadorUsuario(
    codigo_usuario="9930",
    nombre_usuario="MIGUEL GUILLEN",
    # ... sin FK, sin registro en users
)

# DESPUÉS: Sincroniza automáticamente
user_id = UserSyncService.sync_user_from_counter("9930", "MIGUEL GUILLEN", db, printer_id=3)
# Si es la primera vez: Crea el usuario en users automáticamente
# Si ya existe: Usa el user_id existente

contador = ContadorUsuario(
    user_id=user_id,  # ← FK normalizada
    codigo_usuario="9930",  # Mantener para compatibilidad
    nombre_usuario="MIGUEL GUILLEN",
    # ...
)
```

### Caso 2: Reportes de Usuarios Activos por Impresora
```sql
-- ANTES: Difícil, requiere DISTINCT en strings
SELECT DISTINCT codigo_usuario, nombre_usuario
FROM contadores_usuario
WHERE fecha_lectura >= NOW() - INTERVAL '7 days';

-- DESPUÉS: Fácil, usa FK y muestra en qué impresoras está cada usuario
SELECT 
    u.id, 
    u.name, 
    u.codigo_de_usuario, 
    COUNT(DISTINCT cu.printer_id) as impresoras_usadas,
    STRING_AGG(DISTINCT p.hostname, ', ') as nombres_impresoras,
    COUNT(*) as lecturas
FROM users u
JOIN contadores_usuario cu ON u.id = cu.user_id
JOIN printers p ON cu.printer_id = p.id
WHERE cu.fecha_lectura >= NOW() - INTERVAL '7 days'
GROUP BY u.id, u.name, u.codigo_de_usuario
ORDER BY lecturas DESC;

-- Resultado ejemplo:
-- id | name           | codigo | impresoras_usadas | nombres_impresoras                    | lecturas
-- 15 | MIGUEL GUILLEN | 9930   | 5                 | RNP0026737FFBB8, RNP00267391F283, ... | 124
-- 16 | EYMI RODRIGUEZ | 5103   | 4                 | RNP0026737FFBB8, RNP00267391F283, ... | 103
```

### Caso 3: Gestión de Permisos (Centralizada)
```python
# ANTES: Buscar por string, modificar, sin historial de impresoras
user = db.query(User).filter(User.codigo_de_usuario == "9930").first()
if user:
    user.func_printer = True

# DESPUÉS: Mismo código, pero ahora puedes ver en qué impresoras está el usuario
user = db.query(User).filter(User.codigo_de_usuario == "9930").first()
user.func_printer = True  # Habilitar permiso de impresión

# Bonus: Ver historial completo del usuario y sus impresoras
contadores = db.query(ContadorUsuario).filter(
    ContadorUsuario.user_id == user.id
).all()

# Ver en qué impresoras ha usado el usuario
impresoras_usadas = db.query(
    Printer.id,
    Printer.hostname,
    Printer.location,
    func.count(ContadorUsuario.id).label('lecturas')
).join(
    ContadorUsuario, Printer.id == ContadorUsuario.printer_id
).filter(
    ContadorUsuario.user_id == user.id
).group_by(
    Printer.id, Printer.hostname, Printer.location
).all()

# Resultado: Lista de impresoras donde el usuario ha sido detectado
# Útil para saber dónde asignar permisos
```

### Caso 4: Sincronización Masiva Inicial (Una sola vez)
```python
# Script de migración para crear los 429 usuarios faltantes
from backend.services.user_sync_service import UserSyncService

# Sincronizar todos los usuarios detectados en los últimos 30 días
stats = UserSyncService.sync_all_users_from_counters(db, days=30)

print(f"Usuarios creados: {stats['created']}")  # ~429
print(f"Usuarios existentes: {stats['existing']}")  # ~6
print(f"Total usuarios: {stats['total']}")  # ~435

# Después de esto, las lecturas futuras solo crearán usuarios nuevos
```

---

## ⚠️ Consideraciones Importantes

### 1. Usuarios Duplicados
**Problema:** Mismo nombre, diferentes códigos
```
- JUAN LIZARAZO (7104) - Usuario registrado manualmente
- JUAN LIZARAZO (1014) - Usuario detectado en equipo
```

**Solución:** Son usuarios diferentes, se crean ambos. El `codigo_de_usuario` es la clave única que identifica a cada persona.

### 2. Usuarios Inactivos
**Problema:** 429 usuarios detectados, ¿todos activos?

**Solución:** 
- Solo sincronizar usuarios con actividad reciente (últimos 30 días)
- Los históricos se mantienen con `user_id = NULL` pero conservan `codigo_usuario` y `nombre_usuario`
- Según el análisis: 429 usuarios tienen actividad en los últimos 30 días

### 3. Cambios de Nombre
**Problema:** Usuario cambia de nombre en el equipo

**Solución:** 
- El `codigo_de_usuario` es inmutable (clave única)
- Si cambia el nombre, se puede actualizar en `users.name`
- Los registros históricos mantienen el nombre antiguo en `nombre_usuario`

### 4. Eliminación de Usuarios
**Problema:** ¿Qué pasa si se elimina un usuario de `users`?

**Solución:** `ON DELETE SET NULL` - Los registros históricos se mantienen con `user_id = NULL` pero conservan `codigo_usuario` y `nombre_usuario` para referencia.

### 5. Seguimiento de Usuarios por Impresora
**Ventaja adicional:** Con la normalización, ahora es fácil saber:
- En qué impresoras ha sido detectado cada usuario
- Cuántas veces usa cada impresora
- Usuarios activos por impresora
- Asignación automática de permisos por impresora

**Ejemplo de consulta:**
```sql
-- Ver usuarios y sus impresoras
SELECT 
    u.codigo_de_usuario,
    u.name,
    p.hostname,
    p.location,
    COUNT(*) as lecturas,
    MAX(cu.fecha_lectura) as ultima_actividad
FROM users u
JOIN contadores_usuario cu ON u.id = cu.user_id
JOIN printers p ON cu.printer_id = p.id
WHERE cu.fecha_lectura >= NOW() - INTERVAL '7 days'
GROUP BY u.codigo_de_usuario, u.name, p.hostname, p.location
ORDER BY u.name, lecturas DESC;
```

**Resultado:** Lista completa de usuarios con las impresoras que usan, útil para:
- Gestión de permisos por impresora
- Identificar usuarios que usan múltiples equipos
- Reportes de uso por ubicación

---

## 🚀 Plan de Implementación

### Semana 1: Preparación
- [ ] Revisar y aprobar propuesta
- [ ] Crear backup completo de producción
- [ ] Ejecutar migración 012 en ambiente de desarrollo
- [ ] Probar sincronización masiva

### Semana 2: Desarrollo
- [ ] Implementar `UserSyncService`
- [ ] Modificar `counter_service.py`
- [ ] Modificar `cierre_service.py`
- [ ] Crear tests unitarios

### Semana 3: Testing
- [ ] Probar en ambiente de staging
- [ ] Verificar performance de queries
- [ ] Validar integridad de datos
- [ ] Documentar cambios

### Semana 4: Despliegue
- [ ] Ejecutar migración en producción (ventana de mantenimiento)
- [ ] Desplegar código nuevo
- [ ] Monitorear logs y performance
- [ ] Validar con usuarios finales

---

## 📝 Conclusión

Esta propuesta combina:
1. **Normalización de datos** (user_id como FK)
2. **Sincronización automática** (crear usuarios al detectarlos)
3. **Compatibilidad histórica** (mantener campos antiguos)
4. **Mejora de performance** (queries más rápidas)
5. **Mejor gestión** (un solo lugar para usuarios)

**Resultado:** Sistema más eficiente, escalable y fácil de mantener, sin romper funcionalidad existente.

---

**Fecha:** 2026-04-07  
**Versión:** 1.0  
**Estado:** Propuesta para revisión
