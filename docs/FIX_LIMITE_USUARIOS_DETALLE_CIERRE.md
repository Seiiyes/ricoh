# Fix: Límite de 50 Usuarios en Detalle de Cierre

**Fecha**: 25 de marzo de 2026
**Estado**: ✅ RESUELTO
**Problema**: Al visualizar el detalle de un cierre mensual, solo se mostraban 50 usuarios aunque el cierre tuviera más usuarios registrados.

## Problema Identificado

El componente `CierreDetalleModal` intentaba cargar 10,000 usuarios del backend para hacer paginación del lado del cliente, pero solo se estaban cargando 50 usuarios debido a un desajuste en los nombres de parámetros entre el frontend y el backend.

### Evidencia

- Frontend solicitaba: `page=1&limit=10000`
- Backend esperaba: `page=1&page_size=10000`
- Backend recibía `limit` pero lo ignoraba, usando el valor por defecto `page_size=50`
- Resultado: Solo se cargaban 50 usuarios

## Causa Raíz

En `src/services/closeService.ts`, la función `getCloseDetail` enviaba el parámetro `limit`:

```typescript
// Código anterior (INCORRECTO)
getCloseDetail: async (closeId: number, page: number = 1, limit: number = 50): Promise<CierreDetalle> => {
  const response = await apiClient.get<CierreDetalle>(
    `/api/counters/monthly/${closeId}/detail`,
    { params: { page, limit } }  // ❌ Backend espera 'page_size', no 'limit'
  );
  return response.data;
}
```

Pero el backend en `backend/api/counters.py` esperaba `page_size`:

```python
async def get_close_detail(
    cierre_id: int, 
    page: int = 1,
    page_size: int = 50,  # ✅ Backend espera 'page_size'
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
```

## Solución Implementada

Modificado `src/services/closeService.ts` para enviar el parámetro correcto:

```typescript
getCloseDetail: async (closeId: number, page: number = 1, pageSize: number = 50): Promise<CierreDetalle> => {
  const response = await apiClient.get<CierreDetalle>(
    `/api/counters/monthly/${closeId}/detail`,
    { params: { page, page_size: pageSize } }  // ✅ Ahora envía 'page_size'
  );
  return response.data;
}
```

## Comportamiento Esperado

### Antes del Fix ❌
- Frontend solicita: `GET /api/counters/monthly/123/detail?page=1&limit=10000`
- Backend ignora `limit` y usa `page_size=50` por defecto
- Se cargan solo 50 usuarios
- Paginación del lado del cliente no funciona correctamente

### Después del Fix ✅
- Frontend solicita: `GET /api/counters/monthly/123/detail?page=1&page_size=10000`
- Backend recibe `page_size=10000` correctamente
- Se cargan hasta 10,000 usuarios
- Paginación del lado del cliente funciona correctamente
- Se muestran 50 usuarios por página con controles de navegación

## Flujo de Paginación

El sistema usa paginación híbrida:

1. **Backend**: Carga hasta 10,000 usuarios (suficiente para la mayoría de casos)
2. **Frontend**: Pagina los usuarios cargados en grupos de 50
3. **Búsqueda**: Funciona sobre todos los usuarios cargados
4. **Ordenamiento**: Funciona sobre todos los usuarios cargados

### Ventajas de este Enfoque

- ✅ Búsqueda instantánea (no requiere llamadas al backend)
- ✅ Ordenamiento instantáneo (no requiere llamadas al backend)
- ✅ Navegación rápida entre páginas
- ✅ Funciona bien para cierres con hasta 10,000 usuarios

### Limitación

Si un cierre tiene más de 10,000 usuarios (caso extremadamente raro), solo se cargarán los primeros 10,000. Para soportar más usuarios, se podría:
- Aumentar el límite a 50,000 o 100,000
- Implementar paginación del lado del servidor con búsqueda y ordenamiento

## Archivos Modificados

- `src/services/closeService.ts`
  - Cambiado parámetro `limit` a `pageSize`
  - Cambiado envío de `{ params: { page, limit } }` a `{ params: { page, page_size: pageSize } }`

## Pruebas Realizadas

✅ Cierre con 50 usuarios → Se muestran todos correctamente
✅ Cierre con 100 usuarios → Se muestran todos con paginación (2 páginas)
✅ Cierre con 500 usuarios → Se muestran todos con paginación (10 páginas)
✅ Búsqueda funciona sobre todos los usuarios cargados
✅ Ordenamiento funciona sobre todos los usuarios cargados
✅ Controles de paginación se muestran cuando hay más de 50 usuarios

## Notas Técnicas

### Parámetros del Endpoint

```
GET /api/counters/monthly/{cierre_id}/detail
Query Parameters:
  - page: int (default: 1) - Número de página
  - page_size: int (default: 50) - Tamaño de página
  - search: str (optional) - Búsqueda por nombre o código de usuario
```

### Respuesta del Endpoint

```typescript
{
  id: number;
  printer_id: number;
  total_paginas: number;
  usuarios: Array<Usuario>;  // Usuarios de la página solicitada
  total_usuarios: number;    // Total de usuarios en el cierre
  page: number;              // Página actual
  page_size: number;         // Tamaño de página
  total_pages: number;       // Total de páginas
  // ... otros campos
}
```

### Paginación del Lado del Cliente

```typescript
const pageSize = 50;  // Usuarios por página en la UI
const totalPages = Math.ceil(totalFilteredUsers / pageSize);
const startIndex = (currentPage - 1) * pageSize;
const endIndex = startIndex + pageSize;
const paginatedUsuarios = sortedUsuarios.slice(startIndex, endIndex);
```

## Lecciones Aprendidas

1. Siempre verificar que los nombres de parámetros coincidan entre frontend y backend
2. Los valores por defecto en el backend pueden ocultar problemas de parámetros incorrectos
3. La paginación híbrida (backend + cliente) es eficiente para conjuntos de datos medianos
4. Los logs del backend pueden ayudar a identificar qué parámetros se están recibiendo
