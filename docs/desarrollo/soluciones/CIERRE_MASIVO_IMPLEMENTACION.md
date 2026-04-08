# Implementación de Cierre Masivo en Todas las Impresoras

**Fecha:** 2026-04-08  
**Autor:** Sistema de Auditoría  
**Estado:** ✅ Completado

## Resumen

Se implementó la funcionalidad para crear cierres de contadores en todas las impresoras activas simultáneamente, con auditoría completa del usuario que realiza la operación.

## Requisitos Cumplidos

✅ Botón para crear cierres en todas las impresoras simultáneamente  
✅ Mapeo del usuario que hizo el cierre (auditoría)  
✅ Validación de no más de un cierre diario (validación existente se mantiene)  
✅ Tipo de período flexible (diario, semanal, mensual, personalizado)  
✅ Lectura automática de contadores antes de crear cierres  
✅ Filtrado por empresa del usuario actual  
✅ Reporte detallado de éxitos y fallos

## Arquitectura de la Solución

### Backend

#### 1. Servicio: `CloseService.create_close_all_printers()`
**Archivo:** `backend/services/close_service.py`

```python
@staticmethod
def create_close_all_printers(
    db: Session,
    fecha_inicio: date,
    fecha_fin: date,
    tipo_periodo: str = 'personalizado',
    cerrado_por: Optional[str] = None,
    notas: Optional[str] = None,
    empresa_id: Optional[int] = None
) -> Dict:
```

**Funcionalidad:**
- Obtiene todas las impresoras activas (status != 'offline')
- Filtra por empresa_id si se especifica
- Crea cierres para cada impresora usando `create_close()`
- Retorna estadísticas de éxito/fallo
- No valida secuencia en cierres masivos (validar_secuencia=False)

#### 2. Endpoint: `POST /api/counters/close-all`
**Archivo:** `backend/api/counters.py`

**Request Body:**
```json
{
  "tipo_periodo": "diario|semanal|mensual|personalizado",
  "fecha_inicio": "YYYY-MM-DD",
  "fecha_fin": "YYYY-MM-DD",
  "cerrado_por": "Nombre del usuario (opcional)",
  "notas": "Notas adicionales (opcional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Cierres completados: 10 exitosos, 2 fallidos",
  "successful": 10,
  "failed": 2,
  "total": 12,
  "results": [
    {
      "printer_id": 1,
      "printer_name": "RICOH-001",
      "success": true,
      "cierre_id": 123,
      "total_paginas": 50000,
      "usuarios_count": 25,
      "error": null
    },
    {
      "printer_id": 2,
      "printer_name": "RICOH-002",
      "success": false,
      "cierre_id": null,
      "total_paginas": 0,
      "usuarios_count": 0,
      "error": "No hay contadores registrados"
    }
  ]
}
```

**Proceso:**
1. Aplica filtro de empresa del usuario actual
2. Lee contadores de todas las impresoras (total + usuarios)
3. Guarda todas las lecturas en DB (commit)
4. Crea cierres para cada impresora
5. Retorna resumen detallado

#### 3. Schemas
**Archivo:** `backend/api/counter_schemas.py`

```python
class CierreRequest(BaseModel):
    """Para cierre individual"""
    printer_id: int  # REQUERIDO
    tipo_periodo: str
    fecha_inicio: date
    fecha_fin: date
    cerrado_por: Optional[str]
    notas: Optional[str]

class CierreMasivoRequest(BaseModel):
    """Para cierre masivo (sin printer_id)"""
    tipo_periodo: str
    fecha_inicio: date
    fecha_fin: date
    cerrado_por: Optional[str]
    notas: Optional[str]

class CierreResult(BaseModel):
    printer_id: int
    printer_name: str
    success: bool
    cierre_id: Optional[int]
    total_paginas: int
    usuarios_count: int
    error: Optional[str]

class CloseAllPrintersResponse(BaseModel):
    success: bool
    message: str
    successful: int
    failed: int
    total: int
    results: List[CierreResult]
```

### Frontend

#### 1. Modal: `CierreMasivoModal`
**Archivo:** `src/components/contadores/cierres/CierreMasivoModal.tsx`

**Características:**
- Formulario con tipo de período, fechas, usuario y notas
- Advertencia clara sobre operación masiva
- Pantalla de resultados con resumen y detalle por impresora
- Indicadores visuales de éxito/fallo
- Scroll para ver todas las impresoras procesadas

#### 2. Integración en Vista Principal
**Archivo:** `src/components/contadores/cierres/CierresView.tsx`

**Cambios:**
- Agregado botón "Cierre Masivo" al lado de "Nuevo Cierre"
- Importado componente `CierreMasivoModal`
- Agregado estado `cierreMasivoModalOpen`
- Handler `handleCierreMasivoSuccess()` para recargar cierres

#### 3. Servicio
**Archivo:** `src/services/closeService.ts`

```typescript
// Cierre individual (requiere printer_id)
createClose: async (
  data: CreateCloseRequest
): Promise<CierreMensual>

// Cierre masivo (sin printer_id)
createCloseAllPrinters: async (
  data: CreateCierreMasivoRequest
): Promise<CloseAllPrintersResponse>
```

## Flujo de Operación

```
1. Usuario hace clic en "Cierre Masivo"
   ↓
2. Se abre modal con formulario
   ↓
3. Usuario completa:
   - Tipo de período
   - Fecha inicio/fin
   - Cerrado por (auditoría)
   - Notas (opcional)
   ↓
4. Backend recibe request
   ↓
5. Filtra impresoras por empresa del usuario
   ↓
6. Lee contadores de TODAS las impresoras
   ↓
7. Guarda lecturas en DB
   ↓
8. Crea cierres para cada impresora
   ↓
9. Retorna resumen con éxitos/fallos
   ↓
10. Frontend muestra resultados detallados
```

## Validaciones

### Backend
- ✅ Tipo de período válido (diario, semanal, mensual, personalizado)
- ✅ Fecha fin >= fecha inicio
- ✅ Período no mayor a 1 año
- ✅ Período no futuro
- ✅ No existe cierre duplicado del mismo tipo y período
- ✅ Hay contadores registrados hasta fecha_fin
- ✅ No hay reset de contador (comparación con cierre anterior)
- ✅ Filtro de empresa del usuario actual

### Frontend
- ✅ Campos requeridos: tipo_periodo, fecha_inicio, fecha_fin
- ✅ Advertencia clara sobre operación masiva
- ✅ Validación de fechas en formulario HTML5

## Auditoría

El campo `cerrado_por` se guarda en cada cierre creado, permitiendo:
- Rastrear quién realizó cada cierre
- Auditoría completa de operaciones masivas
- Responsabilidad clara en cierres críticos

## Seguridad

- ✅ Filtro automático por empresa del usuario
- ✅ Solo impresoras activas (status != 'offline')
- ✅ Validación de permisos en middleware de autenticación
- ✅ Transacciones atómicas por impresora (fallo en una no afecta otras)

## Manejo de Errores

### Errores Individuales
Si una impresora falla:
- Se registra el error en `results[].error`
- Se continúa con las demás impresoras
- El contador de `failed` se incrementa
- La operación general sigue siendo exitosa

### Errores Comunes
- "No hay contadores registrados": Impresora sin lecturas
- "Ya existe un cierre": Cierre duplicado del mismo tipo/período
- "Reset de contador detectado": Contador menor que cierre anterior
- "No hay impresoras disponibles": Sin impresoras activas con acceso

## Testing

### Casos de Prueba Recomendados

1. **Cierre masivo exitoso**
   - Todas las impresoras tienen contadores
   - No hay cierres duplicados
   - Resultado: 100% éxito

2. **Cierre masivo parcial**
   - Algunas impresoras sin contadores
   - Resultado: Mezcla de éxitos y fallos

3. **Cierre masivo con filtro de empresa**
   - Usuario con empresa_id específica
   - Solo se procesan impresoras de esa empresa

4. **Validación de auditoría**
   - Campo `cerrado_por` se guarda correctamente
   - Se puede rastrear quién hizo cada cierre

5. **Manejo de errores**
   - Impresoras offline se excluyen
   - Cierres duplicados se detectan
   - Resets de contador se reportan

## Archivos Modificados

### Backend
- ✅ `backend/services/close_service.py` (método agregado)
- ✅ `backend/api/counters.py` (endpoint agregado)
- ✅ `backend/api/counter_schemas.py` (schemas agregados)

### Frontend
- ✅ `src/components/contadores/cierres/CierresView.tsx` (botón agregado)
- ✅ `src/components/contadores/cierres/CierreMasivoModal.tsx` (nuevo componente)
- ✅ `src/services/closeService.ts` (método agregado)

## Próximos Pasos

1. ✅ Implementación completada
2. ⏳ Testing en ambiente de desarrollo
3. ⏳ Validación con usuarios finales
4. ⏳ Documentación de usuario final
5. ⏳ Deploy a producción

## Notas Técnicas

- El endpoint lee contadores automáticamente antes de crear cierres
- No se requiere lectura manual previa
- Los snapshots de usuarios se crean con los datos más recientes
- La operación es atómica por impresora (fallo en una no afecta otras)
- El filtro de empresa es automático según el usuario autenticado

## Conclusión

La funcionalidad de cierre masivo está completamente implementada y lista para testing. Cumple con todos los requisitos especificados:
- Auditoría completa del usuario
- Validación de cierres duplicados
- Tipo de período flexible
- Lectura automática de contadores
- Reporte detallado de resultados
