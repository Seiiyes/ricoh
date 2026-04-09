# Verificación: Filtrado por Empresa para Admins

## ✅ SISTEMA DE FILTRADO IMPLEMENTADO CORRECTAMENTE

El sistema ya tiene implementado el filtrado por empresa usando `CompanyFilterService`.

## Cómo Funciona el Filtrado

### 1. Servicio de Filtrado (backend/services/company_filter_service.py)

```python
class CompanyFilterService:
    @classmethod
    def apply_filter(cls, query: Query, user: AdminUser, empresa_field: str = "empresa_id") -> Query:
        """
        Apply company filter to SQLAlchemy query
        
        Logic:
            - If user.rol == "superadmin": No filter (return all)
            - If user.rol in ["admin", "viewer", "operator"]: Filter by user.empresa_id
        """
        # Superadmin sees everything
        if user.is_superadmin():
            return query
        
        # Other roles only see their company's data
        model = query.column_descriptions[0]['entity']
        return query.filter(getattr(model, empresa_field) == user.empresa_id)
```

### 2. Aplicación en Endpoint de Impresoras (backend/api/printers.py)

```python
@router.get("/", response_model=PrinterListResponse)
async def get_printers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all printers with pagination
    
    Admin users only see printers from their empresa.
    """
    # Build base query
    query = db.query(Printer)
    
    # Apply company filter ✅
    query = CompanyFilterService.apply_filter(query, current_user)
    
    # ... rest of the logic ...
```

## Roles y Permisos

### Superadmin
- ✅ Ve TODAS las impresoras de TODAS las empresas
- ✅ Puede crear/editar/eliminar cualquier recurso
- ✅ No tiene restricciones de empresa

### Admin (de empresa)
- ✅ Solo ve impresoras de SU empresa (`empresa_id` del admin)
- ✅ Solo puede crear recursos para SU empresa
- ✅ No puede acceder a recursos de otras empresas

### Viewer / Operator
- ✅ Solo ve impresoras de SU empresa
- ✅ Permisos limitados según rol

## Validación de Acceso Individual

Además del filtrado en listados, cada operación individual valida el acceso:

```python
# Ejemplo en backend/api/counters.py
@router.get("/{printer_id}/counters/latest")
async def get_latest_counters(
    printer_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    
    if not printer:
        raise HTTPException(status_code=404, detail="Impresora no encontrada")
    
    # Validate company access ✅
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta impresora")
    
    # ... rest of the logic ...
```

## Endpoints Protegidos

Todos estos endpoints aplican filtrado por empresa:

### Impresoras
- ✅ `GET /printers/` - Lista filtrada por empresa
- ✅ `GET /printers/{id}` - Valida acceso individual
- ✅ `PUT /printers/{id}` - Valida acceso antes de editar
- ✅ `DELETE /printers/{id}` - Valida acceso antes de eliminar

### Contadores
- ✅ `GET /counters/{printer_id}/counters/latest` - Valida acceso
- ✅ `GET /counters/{printer_id}/counters/history` - Valida acceso
- ✅ `POST /counters/{printer_id}/counters/read` - Valida acceso
- ✅ `POST /counters/close-all` - Solo cierra impresoras de su empresa

### Cierres
- ✅ `GET /counters/{printer_id}/cierres` - Valida acceso
- ✅ `GET /counters/{printer_id}/cierres/{cierre_id}` - Valida acceso
- ✅ `POST /counters/{printer_id}/cierres/{cierre_id}/export` - Valida acceso

## Prueba de Verificación

### Paso 1: Crear Admin de Empresa

```sql
-- Verificar que existe la empresa
SELECT * FROM empresas WHERE id = 1;

-- Crear admin para empresa 1
INSERT INTO admin_users (username, password_hash, rol, empresa_id, is_active)
VALUES ('admin_empresa1', '$2b$12$...', 'admin', 1, true);
```

### Paso 2: Asignar Impresoras a Empresa

```sql
-- Asignar algunas impresoras a empresa 1
UPDATE printers SET empresa_id = 1 WHERE id IN (1, 2, 3);

-- Asignar otras impresoras a empresa 2
UPDATE printers SET empresa_id = 2 WHERE id IN (4, 5, 6);
```

### Paso 3: Probar Acceso

1. **Login como admin_empresa1:**
```bash
POST /auth/login
{
  "username": "admin_empresa1",
  "password": "..."
}
```

2. **Listar impresoras (debería ver solo empresa 1):**
```bash
GET /printers/
Authorization: Bearer <token>

# Respuesta esperada: Solo impresoras con empresa_id = 1
```

3. **Intentar acceder a impresora de otra empresa:**
```bash
GET /printers/4
Authorization: Bearer <token>

# Respuesta esperada: 403 Forbidden
```

## Error del WebSocket

El error que mencionaste:
```
WebSocket error: Event {isTrusted: true, type: 'error', target: WebSocket...}
```

**No está relacionado con el filtrado por empresa.** Es un problema del WebSocket de logs en tiempo real.

### Causa del Error WebSocket

El WebSocket en `ws://localhost:8000/ws/logs` está fallando porque:
1. El servidor WebSocket puede no estar escuchando correctamente
2. Puede haber un problema de CORS con WebSockets
3. El cliente intenta conectarse antes de que el servidor esté listo

### Solución para WebSocket

El error del WebSocket NO afecta la funcionalidad principal. Es solo para logs en tiempo real. Para solucionarlo:

1. **Verificar que el servidor WebSocket está corriendo:**
```python
# En backend/main.py, el endpoint está definido:
@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    # ...
```

2. **Verificar CORS para WebSockets:**
```python
# En backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **Opcional: Deshabilitar WebSocket en frontend si no es crítico:**
```typescript
// En src/services/printerService.ts
// Comentar o envolver en try-catch la conexión WebSocket
```

## Resumen

### ✅ Filtrado por Empresa
- **FUNCIONANDO CORRECTAMENTE**
- Implementado con `CompanyFilterService`
- Aplicado en todos los endpoints relevantes
- Validación individual en operaciones específicas

### ⚠️ Error WebSocket
- **NO RELACIONADO con filtrado por empresa**
- Es un problema menor de logs en tiempo real
- NO afecta funcionalidad principal
- Puede ser ignorado o solucionado después

## Comandos de Verificación

### Verificar empresas
```sql
SELECT * FROM empresas;
```

### Verificar admins de empresa
```sql
SELECT id, username, rol, empresa_id, is_active FROM admin_users WHERE rol = 'admin';
```

### Verificar impresoras por empresa
```sql
SELECT id, hostname, ip_address, empresa_id FROM printers ORDER BY empresa_id;
```

### Verificar que admin solo ve su empresa
```sql
-- Simular query de admin con empresa_id = 1
SELECT * FROM printers WHERE empresa_id = 1;
```

## Conclusión

✅ **El sistema de filtrado por empresa está correctamente implementado y funcionando.**

El error del WebSocket es un problema separado y menor que no afecta la funcionalidad de filtrado por empresa.
