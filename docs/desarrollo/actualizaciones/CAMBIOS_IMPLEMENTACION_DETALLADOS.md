# Cambios Detallados para Implementación de Normalización

## 📋 Resumen
Este documento detalla TODOS los cambios necesarios en backend, frontend y base de datos para implementar la normalización con sincronización automática de usuarios.

---

## 🗄️ CAMBIOS EN BASE DE DATOS

### 1. Ejecutar Migración 012
**Archivo:** `backend/migrations/012_normalize_user_references.sql`  
**Estado:** ✅ Ya existe, listo para ejecutar

**Qué hace:**
- Agrega columna `user_id` a `contadores_usuario`
- Agrega columna `user_id` a `cierres_mensuales_usuarios`
- Crea índices para performance
- Agrega FK constraints
- Crea vistas de compatibilidad
- Sincroniza usuarios existentes

**Comando:**
```bash
Get-Content backend/migrations/012_normalize_user_references.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
```

**Resultado esperado:**
- Columnas `user_id` agregadas
- ~6 usuarios con `user_id` poblado (los que ya existen)
- ~21,350 registros en `contadores_usuario` con `user_id = NULL` (históricos)
- ~6,770 registros en `cierres_mensuales_usuarios` con `user_id = NULL` (históricos)

---

## 🐍 CAMBIOS EN BACKEND

### 1. Modelos SQLAlchemy

#### `backend/db/models.py` - Clase `ContadorUsuario`

**ANTES:**
```python
class ContadorUsuario(Base):
    __tablename__ = "contadores_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usuario
    codigo_usuario = Column(String(8), nullable=False, index=True)
    nombre_usuario = Column(String(100), nullable=False)
    
    # ... resto de campos
    
    # Relationships
    printer = relationship("Printer")
```

**DESPUÉS:**
```python
class ContadorUsuario(Base):
    __tablename__ = "contadores_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usuario (normalizado)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # ← NUEVO
    codigo_usuario = Column(String(8), nullable=False, index=True)  # Mantener para compatibilidad
    nombre_usuario = Column(String(100), nullable=False)  # Mantener para compatibilidad
    
    # ... resto de campos
    
    # Relationships
    printer = relationship("Printer")
    user = relationship("User")  # ← NUEVO
```

#### `backend/db/models.py` - Clase `CierreMensualUsuario`

**ANTES:**
```python
class CierreMensualUsuario(Base):
    __tablename__ = "cierres_mensuales_usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    cierre_mensual_id = Column(Integer, ForeignKey("cierres_mensuales.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usuario
    codigo_usuario = Column(String(8), nullable=False, index=True)
    nombre_usuario = Column(String(100), nullable=False)
    
    # ... resto de campos
    
    # Relationships
    cierre = relationship("CierreMensual", back_populates="usuarios")
```

**DESPUÉS:**
```python
class CierreMensualUsuario(Base):
    __tablename__ = "cierres_mensuales_usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    cierre_mensual_id = Column(Integer, ForeignKey("cierres_mensuales.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Usuario (normalizado)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # ← NUEVO
    codigo_usuario = Column(String(8), nullable=False, index=True)  # Mantener para compatibilidad
    nombre_usuario = Column(String(100), nullable=False)  # Mantener para compatibilidad
    
    # ... resto de campos
    
    # Relationships
    cierre = relationship("CierreMensual", back_populates="usuarios")
    user = relationship("User")  # ← NUEVO
```

---

### 2. Crear Servicio de Sincronización

#### `backend/services/user_sync_service.py` (NUEVO ARCHIVO)

```python
"""
Servicio para sincronizar usuarios detectados en equipos con la tabla users.
Implementa sincronización automática al leer contadores.
"""

from sqlalchemy.orm import Session
from backend.db.models import User, ContadorUsuario
from backend.logger import logger
from datetime import datetime, timedelta
from typing import Optional


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
        printer_id: Optional[int] = None
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

---

### 3. Modificar Parsers de Contadores

#### `backend/services/parsers/user_counter_parser.py`

**Buscar todas las líneas donde se crea `user_data` y NO CAMBIAR NADA.**

Los parsers deben seguir retornando `codigo_usuario` y `nombre_usuario` como texto.
La sincronización se hace en el servicio que guarda los contadores.

**NO REQUIERE CAMBIOS** ✅

---

### 4. Modificar Servicio de Contadores

#### `backend/api/counters.py` - Endpoint de guardado

**ANTES:**
```python
@router.post("/{printer_id}/user-counters", response_model=List[UserCounterResponse])
async def save_user_counters(
    printer_id: int,
    counters: List[UserCounterCreate],
    db: Session = Depends(get_db)
):
    """Guardar contadores de usuario"""
    saved_counters = []
    
    for counter_data in counters:
        # Crear contador directamente
        contador = ContadorUsuario(
            printer_id=printer_id,
            codigo_usuario=counter_data.codigo_usuario,
            nombre_usuario=counter_data.nombre_usuario,
            # ... resto de campos
        )
        db.add(contador)
        saved_counters.append(contador)
    
    db.commit()
    return saved_counters
```

**DESPUÉS:**
```python
from backend.services.user_sync_service import UserSyncService  # ← NUEVO IMPORT

@router.post("/{printer_id}/user-counters", response_model=List[UserCounterResponse])
async def save_user_counters(
    printer_id: int,
    counters: List[UserCounterCreate],
    db: Session = Depends(get_db)
):
    """Guardar contadores de usuario con sincronización automática"""
    saved_counters = []
    
    for counter_data in counters:
        # ✓ NUEVO: Sincronizar usuario automáticamente
        user_id = UserSyncService.sync_user_from_counter(
            codigo_usuario=counter_data.codigo_usuario,
            nombre_usuario=counter_data.nombre_usuario,
            printer_id=printer_id,
            db=db
        )
        
        # Crear contador con FK normalizada
        contador = ContadorUsuario(
            printer_id=printer_id,
            user_id=user_id,  # ← NUEVO: FK normalizada
            codigo_usuario=counter_data.codigo_usuario,  # Mantener para compatibilidad
            nombre_usuario=counter_data.nombre_usuario,  # Mantener para compatibilidad
            # ... resto de campos
        )
        db.add(contador)
        saved_counters.append(contador)
    
    db.commit()
    return saved_counters
```

---

### 5. Modificar Servicio de Cierres

#### `backend/services/close_service.py` - Función `calcular_consumo_usuario`

**ANTES:**
```python
def calcular_consumo_usuario(
    db: Session,
    printer_id: int,
    codigo_usuario: str,
    fecha_inicio: date,
    fecha_fin: date,
    cierre_anterior: Optional[CierreMensual] = None
) -> dict:
    """Calcular consumo de un usuario en un período"""
    
    # Buscar contador actual
    contador_actual = db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.codigo_usuario == codigo_usuario,
        # ...
    ).first()
    
    # Buscar contador anterior en cierre previo
    if cierre_anterior:
        contador_anterior = db.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre_anterior.id,
            CierreMensualUsuario.codigo_usuario == codigo_usuario
        ).first()
    
    # ... resto de lógica
```

**DESPUÉS:**
```python
from backend.services.user_sync_service import UserSyncService  # ← NUEVO IMPORT

def calcular_consumo_usuario(
    db: Session,
    printer_id: int,
    codigo_usuario: str,
    fecha_inicio: date,
    fecha_fin: date,
    cierre_anterior: Optional[CierreMensual] = None
) -> dict:
    """Calcular consumo de un usuario en un período"""
    
    # Buscar contador actual
    contador_actual = db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.codigo_usuario == codigo_usuario,
        # ...
    ).first()
    
    if not contador_actual:
        return None
    
    # ✓ NUEVO: Obtener user_id (puede ser None para registros históricos)
    user_id = contador_actual.user_id
    
    # Si no tiene user_id, intentar sincronizar
    if not user_id:
        user_id = UserSyncService.sync_user_from_counter(
            codigo_usuario=codigo_usuario,
            nombre_usuario=contador_actual.nombre_usuario,
            printer_id=printer_id,
            db=db
        )
    
    # Buscar contador anterior en cierre previo
    # Intentar primero por user_id, luego por codigo_usuario
    contador_anterior = None
    if cierre_anterior:
        if user_id:
            contador_anterior = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == cierre_anterior.id,
                CierreMensualUsuario.user_id == user_id  # ← NUEVO: Buscar por FK
            ).first()
        
        # Fallback: buscar por codigo_usuario (para registros históricos)
        if not contador_anterior:
            contador_anterior = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == cierre_anterior.id,
                CierreMensualUsuario.codigo_usuario == codigo_usuario
            ).first()
    
    # ... resto de lógica (sin cambios)
    
    return {
        'codigo_usuario': codigo_usuario,
        'nombre_usuario': contador_actual.nombre_usuario,
        'user_id': user_id,  # ← NUEVO: Incluir en resultado
        # ... resto de campos
    }
```

#### `backend/services/close_service.py` - Función `crear_cierre_mensual`

**ANTES:**
```python
# Crear snapshot de usuarios
for consumo in consumos_usuarios:
    usuario_cierre = CierreMensualUsuario(
        cierre_mensual_id=cierre.id,
        codigo_usuario=consumo['codigo_usuario'],
        nombre_usuario=consumo['nombre_usuario'],
        # ... resto de campos
    )
    db.add(usuario_cierre)
```

**DESPUÉS:**
```python
# Crear snapshot de usuarios
for consumo in consumos_usuarios:
    usuario_cierre = CierreMensualUsuario(
        cierre_mensual_id=cierre.id,
        user_id=consumo.get('user_id'),  # ← NUEVO: FK normalizada (puede ser None)
        codigo_usuario=consumo['codigo_usuario'],  # Mantener para compatibilidad
        nombre_usuario=consumo['nombre_usuario'],  # Mantener para compatibilidad
        # ... resto de campos
    )
    db.add(usuario_cierre)
```

---

### 6. Schemas Pydantic (NO REQUIEREN CAMBIOS)

Los schemas en `backend/api/counter_schemas.py` NO necesitan cambios porque:
- El frontend sigue enviando `codigo_usuario` y `nombre_usuario`
- El backend los recibe y sincroniza internamente
- Las respuestas siguen incluyendo `codigo_usuario` y `nombre_usuario` para compatibilidad

**NO REQUIERE CAMBIOS** ✅

---

## ⚛️ CAMBIOS EN FRONTEND

### ¡BUENAS NOTICIAS! 🎉

**EL FRONTEND NO REQUIERE CAMBIOS**

¿Por qué?
1. El backend sigue aceptando `codigo_usuario` y `nombre_usuario` en las peticiones
2. El backend sigue retornando `codigo_usuario` y `nombre_usuario` en las respuestas
3. La sincronización es transparente (ocurre internamente en el backend)
4. Los campos antiguos se mantienen para compatibilidad

### Archivos que NO necesitan cambios:
- ✅ `src/types/counter.ts` - Sigue usando `codigo_usuario`
- ✅ `src/types/usuario.ts` - Sigue usando `codigo_de_usuario`
- ✅ `src/components/contadores/**` - Sin cambios
- ✅ `src/components/usuarios/**` - Sin cambios
- ✅ `src/services/**` - Sin cambios

---

## 📊 RESUMEN DE CAMBIOS

### Base de Datos
- ✅ Ejecutar migración 012 (agrega columnas `user_id`)

### Backend - Archivos a CREAR
1. ✅ `backend/services/user_sync_service.py` (NUEVO)

### Backend - Archivos a MODIFICAR
1. ✅ `backend/db/models.py`
   - Clase `ContadorUsuario`: Agregar `user_id` y relación
   - Clase `CierreMensualUsuario`: Agregar `user_id` y relación

2. ✅ `backend/api/counters.py`
   - Endpoint `save_user_counters`: Agregar sincronización automática

3. ✅ `backend/services/close_service.py`
   - Función `calcular_consumo_usuario`: Usar `user_id` cuando esté disponible
   - Función `crear_cierre_mensual`: Guardar `user_id` en snapshot

### Backend - Archivos SIN CAMBIOS
- ✅ `backend/services/parsers/user_counter_parser.py`
- ✅ `backend/api/counter_schemas.py`
- ✅ `backend/api/export.py`

### Frontend
- ✅ **NINGÚN CAMBIO NECESARIO** 🎉

---

## 🧪 PLAN DE TESTING

### 1. Tests Unitarios (Nuevos)
```python
# backend/tests/test_user_sync_service.py

def test_sync_user_from_counter_creates_new_user():
    """Debe crear usuario si no existe"""
    user_id = UserSyncService.sync_user_from_counter(
        codigo_usuario="9999",
        nombre_usuario="TEST USER",
        db=db
    )
    assert user_id is not None
    
    user = db.query(User).filter(User.id == user_id).first()
    assert user.codigo_de_usuario == "9999"
    assert user.name == "TEST USER"
    assert user.func_copier == False  # Permisos deshabilitados

def test_sync_user_from_counter_returns_existing_user():
    """Debe retornar usuario existente si ya está creado"""
    # Crear usuario
    user_id_1 = UserSyncService.sync_user_from_counter(
        codigo_usuario="9999",
        nombre_usuario="TEST USER",
        db=db
    )
    
    # Intentar crear de nuevo
    user_id_2 = UserSyncService.sync_user_from_counter(
        codigo_usuario="9999",
        nombre_usuario="TEST USER",
        db=db
    )
    
    assert user_id_1 == user_id_2  # Debe ser el mismo ID
```

### 2. Tests de Integración
```python
# backend/tests/test_counter_integration.py

def test_save_user_counters_creates_users_automatically():
    """Debe crear usuarios automáticamente al guardar contadores"""
    # Guardar contadores de usuario nuevo
    response = client.post(
        f"/api/counters/{printer_id}/user-counters",
        json=[{
            "codigo_usuario": "9999",
            "nombre_usuario": "TEST USER",
            "total_paginas": 100,
            # ... resto de campos
        }]
    )
    
    assert response.status_code == 200
    
    # Verificar que usuario se creó
    user = db.query(User).filter(
        User.codigo_de_usuario == "9999"
    ).first()
    assert user is not None
    assert user.name == "TEST USER"
    
    # Verificar que contador tiene user_id
    contador = db.query(ContadorUsuario).filter(
        ContadorUsuario.codigo_usuario == "9999"
    ).first()
    assert contador.user_id == user.id
```

### 3. Tests Manuales
1. ✅ Leer contadores desde impresora real
2. ✅ Verificar que usuarios nuevos se crean automáticamente
3. ✅ Verificar que `user_id` se guarda en contadores
4. ✅ Crear cierre mensual
5. ✅ Verificar que cierre usa `user_id`
6. ✅ Verificar reportes funcionan correctamente

---

## 🚀 ORDEN DE IMPLEMENTACIÓN

### Día 1: Base de Datos
1. Crear backup de producción
2. Ejecutar migración 012 en desarrollo
3. Verificar que migración completó exitosamente

### Día 2-3: Backend - Servicio de Sincronización
1. Crear `backend/services/user_sync_service.py`
2. Crear tests unitarios
3. Ejecutar tests

### Día 4-5: Backend - Modelos y Contadores
1. Modificar `backend/db/models.py`
2. Modificar `backend/api/counters.py`
3. Crear tests de integración
4. Ejecutar tests

### Día 6-7: Backend - Cierres
1. Modificar `backend/services/close_service.py`
2. Crear tests de integración
3. Ejecutar tests

### Día 8-9: Testing Completo
1. Tests de integración completos
2. Tests manuales con impresoras reales
3. Validación de performance

### Día 10: Despliegue
1. Ejecutar migración 012 en producción
2. Desplegar código nuevo
3. Monitorear logs
4. Validar con usuarios finales

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Pre-Implementación
- [ ] Backup de producción creado
- [ ] Migración 012 probada en desarrollo
- [ ] Equipo técnico informado

### Desarrollo
- [ ] `user_sync_service.py` creado
- [ ] `models.py` modificado
- [ ] `counters.py` modificado
- [ ] `close_service.py` modificado
- [ ] Tests unitarios creados
- [ ] Tests de integración creados
- [ ] Todos los tests pasando

### Testing
- [ ] Lectura de contadores probada
- [ ] Sincronización automática validada
- [ ] Creación de cierres probada
- [ ] Reportes validados
- [ ] Performance validada

### Despliegue
- [ ] Migración 012 ejecutada en producción
- [ ] Código desplegado
- [ ] Logs monitoreados
- [ ] Validación con usuarios finales

---

**Fecha:** 2026-04-07  
**Versión:** 1.0  
**Estado:** Listo para implementación
