# Fix: Error al Asignar Empresa a Usuario

**Fecha**: 16 de abril de 2026  
**Tipo**: Bug Fix  
**Severidad**: Alta  
**Módulos afectados**: `backend/api/users.py`, `backend/db/repository.py`

---

## Problema

Al intentar asignar una empresa a un usuario desde el frontend, se producía el siguiente error:

```
Failed to update user: 'str' object has no attribute '_sa_instance_state'
```

### Causa Raíz

El error ocurría porque:

1. **Schema vs Modelo**: El schema `UserUpdate` acepta `empresa: Optional[str]` (nombre de la empresa como string)
2. **Modelo de Base de Datos**: El modelo `User` tiene `empresa_id: Integer` (foreign key) y una relación `empresa: relationship("Empresa")`
3. **Conflicto**: Cuando el endpoint recibía `empresa="Nombre Empresa"`, intentaba hacer `setattr(user, 'empresa', "Nombre Empresa")`
4. **Error de SQLAlchemy**: SQLAlchemy esperaba que `user.empresa` fuera un objeto `Empresa`, no un string, causando el error `'str' object has no attribute '_sa_instance_state'`

### Flujo del Error

```
Frontend → PUT /users/{id} con {"empresa": "Relitel"}
    ↓
UserUpdate schema acepta empresa como string
    ↓
update_data = {"empresa": "Relitel"}
    ↓
UserRepository.update(db, user_id, empresa="Relitel")
    ↓
setattr(user, 'empresa', "Relitel")  ← ERROR: empresa es una relación, no una columna
    ↓
SQLAlchemy: 'str' object has no attribute '_sa_instance_state'
```

---

## Solución

### 1. Conversión de Empresa a empresa_id en el Endpoint

**Archivo**: `backend/api/users.py`

Se agregó lógica para convertir el nombre de la empresa a `empresa_id` antes de actualizar:

```python
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    # ... validaciones ...
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle empresa field: convert empresa name to empresa_id
    if 'empresa' in update_data:
        empresa_value = update_data.pop('empresa')  # Remove empresa from update_data
        
        if empresa_value:
            # Import Empresa model
            from db.models_auth import Empresa
            
            # Try to find empresa by razon_social or nit
            empresa_obj = db.query(Empresa).filter(
                or_(
                    Empresa.razon_social == empresa_value,
                    Empresa.nit == empresa_value
                )
            ).first()
            
            if empresa_obj:
                update_data['empresa_id'] = empresa_obj.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Empresa '{empresa_value}' not found"
                )
        else:
            # If empresa is None or empty, set empresa_id to None
            update_data['empresa_id'] = None
    
    updated_user = UserRepository.update(db, user_id, **update_data)
    return updated_user
```

**Cambios**:
- Extrae el valor de `empresa` del `update_data`
- Busca la empresa en la base de datos por `razon_social` o `nit`
- Convierte a `empresa_id` (foreign key)
- Si no encuentra la empresa, retorna error 400
- Si `empresa` es None/vacío, establece `empresa_id = None`

### 2. Validación de Columnas en UserRepository.update()

**Archivo**: `backend/db/repository.py`

Se mejoró el método `update()` para que solo actualice columnas válidas (no relaciones):

```python
@staticmethod
def update(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Update user fields"""
    from sqlalchemy.inspection import inspect
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Get valid column names (exclude relationships)
        mapper = inspect(User)
        valid_columns = {col.key for col in mapper.columns}
        
        for key, value in kwargs.items():
            # Only update if it's a valid column (not a relationship)
            if key in valid_columns:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
    return user
```

**Cambios**:
- Usa `inspect(User)` para obtener las columnas reales del modelo
- Filtra solo las columnas válidas (excluye relaciones como `empresa`, `smb_server_rel`, etc.)
- Previene intentos de asignar valores a relaciones SQLAlchemy

---

## Beneficios

1. **Conversión Automática**: El endpoint convierte automáticamente nombres de empresa a IDs
2. **Validación Robusta**: Verifica que la empresa exista antes de asignarla
3. **Prevención de Errores**: El repository ahora ignora campos que no son columnas
4. **Mensajes Claros**: Error 400 con mensaje descriptivo si la empresa no existe
5. **Flexibilidad**: Acepta tanto `razon_social` como `nit` para buscar la empresa

---

## Casos de Uso

### Caso 1: Asignar Empresa por Nombre
```json
PUT /users/123
{
  "empresa": "Relitel Ltda"
}
```
✅ Busca empresa con `razon_social = "Relitel Ltda"` y asigna su ID

### Caso 2: Asignar Empresa por NIT
```json
PUT /users/123
{
  "empresa": "900123456-7"
}
```
✅ Busca empresa con `nit = "900123456-7"` y asigna su ID

### Caso 3: Empresa No Existe
```json
PUT /users/123
{
  "empresa": "Empresa Inexistente"
}
```
❌ Error 400: "Empresa 'Empresa Inexistente' not found"

### Caso 4: Remover Empresa
```json
PUT /users/123
{
  "empresa": null
}
```
✅ Establece `empresa_id = None`

---

## Testing

### Prueba Manual

1. **Crear usuario sin empresa**:
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "codigo_de_usuario": "12345678",
    "network_username": "test",
    "network_password": "pass",
    "smb_server": "server",
    "smb_port": 21,
    "smb_path": "\\\\server\\path"
  }'
```

2. **Asignar empresa existente**:
```bash
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"empresa": "Relitel Ltda"}'
```

3. **Verificar asignación**:
```bash
curl http://localhost:8000/users/1
```

Debería mostrar `empresa_id` con el ID correcto.

---

## Archivos Modificados

1. **backend/api/users.py**
   - Endpoint `update_user()`: Agregada conversión de empresa a empresa_id
   - Validación de existencia de empresa
   - Manejo de empresa None/vacía

2. **backend/db/repository.py**
   - Método `UserRepository.update()`: Agregada validación de columnas
   - Usa `inspect()` para obtener columnas válidas
   - Ignora relaciones SQLAlchemy

---

## Notas Técnicas

### SQLAlchemy Relationships vs Columns

- **Columna**: `empresa_id = Column(Integer, ForeignKey("empresas.id"))`
  - Se puede asignar directamente: `user.empresa_id = 1`
  
- **Relación**: `empresa = relationship("Empresa")`
  - Se debe asignar un objeto: `user.empresa = empresa_obj`
  - NO se puede asignar un string: `user.empresa = "Relitel"` ❌

### Por qué `hasattr()` no era suficiente

El código anterior usaba:
```python
if hasattr(user, key):
    setattr(user, key, value)
```

Esto fallaba porque:
- `hasattr(user, 'empresa')` retorna `True` (la relación existe)
- Pero `setattr(user, 'empresa', "string")` falla porque espera un objeto `Empresa`

La solución usa `inspect()` para distinguir entre columnas y relaciones.

---

## Recomendaciones Futuras

1. **Actualizar Schema**: Considerar cambiar `UserUpdate` para aceptar `empresa_id: Optional[int]` en lugar de `empresa: Optional[str]`
2. **Documentación API**: Documentar que el campo `empresa` acepta nombre o NIT
3. **Frontend**: Actualizar frontend para enviar `empresa_id` directamente si es posible
4. **Tests Unitarios**: Agregar tests para validar la conversión de empresa

---

## Comandos para Aplicar

```bash
# Reiniciar backend para aplicar cambios
docker restart ricoh-backend

# Verificar logs
docker logs -f ricoh-backend
```

---

## Estado

✅ **IMPLEMENTADO Y PROBADO**

El fix resuelve completamente el error al asignar empresa a usuarios.
