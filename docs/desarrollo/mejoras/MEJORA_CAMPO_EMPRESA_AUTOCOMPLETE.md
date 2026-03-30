# Mejora: Campo Empresa con Autocompletado

**Fecha:** 20 de Marzo de 2026  
**Tipo:** Feature Enhancement  
**Prioridad:** Media

---

## Objetivo

Mejorar la experiencia de usuario al seleccionar empresas en formularios, reemplazando inputs de texto libre por un componente de autocompletado con búsqueda en tiempo real.

---

## Problema Anterior

### Inputs de Texto Libre
Los campos de empresa eran inputs de texto libre donde el usuario debía escribir manualmente el nombre de la empresa:

```tsx
<Input
  label="Empresa"
  value={empresa}
  onChange={(e) => setEmpresa(e.target.value)}
  placeholder="Ej: ACME Corp"
/>
```

### Problemas Identificados:
1. ❌ **Inconsistencia de datos** - Usuarios escribían nombres diferentes para la misma empresa
2. ❌ **Errores tipográficos** - Nombres mal escritos
3. ❌ **No se aprovechan empresas existentes** - Usuario no sabe qué empresas ya existen
4. ❌ **Mala UX** - Usuario debe recordar nombres exactos

---

## Solución Implementada

### Componente EmpresaAutocomplete

Se creó un componente reutilizable de autocompletado con las siguientes características:

#### Características Principales:
1. ✅ **Búsqueda en tiempo real** - Filtra empresas mientras el usuario escribe
2. ✅ **Dropdown con lista de empresas** - Muestra empresas existentes
3. ✅ **Límite de 50 resultados** - Optimizado para rendimiento
4. ✅ **Información completa** - Muestra razón social, nombre comercial y NIT
5. ✅ **Permite texto libre** - Usuario puede escribir si la empresa no existe
6. ✅ **Botón de limpiar** - Fácil borrado del valor
7. ✅ **Responsive** - Se adapta a diferentes tamaños de pantalla
8. ✅ **Accesible** - Cierra al hacer click fuera

#### Optimizaciones de Rendimiento:
- **Límite de 50 empresas** - Evita cargar cientos de registros
- **Búsqueda en backend** - Filtrado eficiente en base de datos
- **Lazy loading** - Solo carga cuando se abre el dropdown
- **Debounce implícito** - React maneja el estado de búsqueda

---

## Implementación Técnica

### 1. Componente Creado

**Archivo:** `src/components/ui/EmpresaAutocomplete.tsx`

```typescript
interface EmpresaAutocompleteProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
}
```

**Características del componente:**
- Usa `empresaService.getAll()` con paginación
- Límite de 50 resultados por búsqueda
- Búsqueda en tiempo real con parámetro `search`
- Dropdown con scroll para muchos resultados
- Input de búsqueda dentro del dropdown

### 2. Integración en Formularios

#### EditPrinterModal.tsx
```tsx
// ANTES
<Input
  label="Empresa"
  value={empresa}
  onChange={(e) => setEmpresa(e.target.value)}
  placeholder="Ej: ACME Corp"
/>

// DESPUÉS
<EmpresaAutocomplete
  label="Empresa"
  value={empresa}
  onChange={setEmpresa}
  placeholder="Buscar o seleccionar empresa..."
/>
```

#### ModificarUsuario.tsx
```tsx
// ANTES
<Input
  value={empresa}
  onChange={(e) => setEmpresa(e.target.value)}
  className="font-bold"
/>

// DESPUÉS
<EmpresaAutocomplete
  label="Empresa"
  value={empresa}
  onChange={setEmpresa}
  placeholder="Buscar o seleccionar empresa..."
/>
```

---

## Archivos Modificados

### Nuevos Archivos:
1. `src/components/ui/EmpresaAutocomplete.tsx` - Componente de autocompletado

### Archivos Modificados:
1. `src/components/ui/index.ts` - Export del nuevo componente
2. `src/components/fleet/EditPrinterModal.tsx` - Uso en modal de impresoras
3. `src/components/usuarios/ModificarUsuario.tsx` - Uso en formulario de usuarios

---

## Uso del Componente

### Ejemplo Básico
```tsx
import { EmpresaAutocomplete } from '@/components/ui';

function MiFormulario() {
  const [empresa, setEmpresa] = useState('');

  return (
    <EmpresaAutocomplete
      label="Empresa"
      value={empresa}
      onChange={setEmpresa}
      placeholder="Buscar o seleccionar empresa..."
    />
  );
}
```

### Con Validación
```tsx
<EmpresaAutocomplete
  label="Empresa"
  value={empresa}
  onChange={setEmpresa}
  required
  error={!empresa ? 'La empresa es requerida' : undefined}
/>
```

### Deshabilitado
```tsx
<EmpresaAutocomplete
  label="Empresa"
  value={empresa}
  onChange={setEmpresa}
  disabled={true}
/>
```

---

## Flujo de Usuario

### 1. Usuario Abre el Dropdown
- Click en el input o en el botón de chevron
- Se cargan las primeras 50 empresas
- Se muestra un input de búsqueda

### 2. Usuario Busca
- Escribe en el input de búsqueda
- Backend filtra empresas por razón social, nombre comercial o NIT
- Se muestran hasta 50 resultados

### 3. Usuario Selecciona
- Click en una empresa de la lista
- El valor se actualiza en el input principal
- El dropdown se cierra

### 4. Usuario Escribe Texto Libre (Opcional)
- Escribe directamente en el input principal
- El valor se guarda aunque no exista en la lista
- Útil para empresas nuevas que aún no están registradas

---

## Beneficios

### Para el Usuario:
1. ✅ **Más rápido** - Seleccionar de lista es más rápido que escribir
2. ✅ **Menos errores** - No hay errores tipográficos
3. ✅ **Descubrimiento** - Ve qué empresas ya existen
4. ✅ **Información completa** - Ve razón social, nombre comercial y NIT

### Para el Sistema:
1. ✅ **Datos consistentes** - Nombres de empresas estandarizados
2. ✅ **Mejor rendimiento** - Límite de 50 resultados
3. ✅ **Búsqueda eficiente** - Filtrado en backend
4. ✅ **Reutilizable** - Componente puede usarse en cualquier formulario

---

## Consideraciones de Rendimiento

### Límite de 50 Empresas
- **Razón:** Evitar cargar cientos de registros en el dropdown
- **Solución:** Mensaje al usuario: "Mostrando primeras 50 empresas. Use la búsqueda para filtrar."
- **Impacto:** Carga rápida incluso con muchas empresas en la BD

### Búsqueda en Backend
- **Endpoint:** `GET /empresas?search={term}&page_size=50`
- **Ventaja:** Filtrado eficiente en PostgreSQL con índices
- **Alternativa descartada:** Cargar todas y filtrar en frontend (ineficiente)

### Lazy Loading
- **Comportamiento:** Solo carga empresas cuando se abre el dropdown
- **Ventaja:** No hace requests innecesarios
- **Implementación:** `useEffect` con dependencia en `isOpen`

---

## Mejoras Futuras (Opcional)

### 1. Debounce en Búsqueda
Agregar debounce de 300ms para evitar requests excesivos:
```typescript
import { useDebouncedValue } from '@/hooks/useDebounce';

const debouncedSearch = useDebouncedValue(searchTerm, 300);
```

### 2. Cache de Resultados
Cachear resultados de búsqueda para evitar requests duplicados:
```typescript
const [cache, setCache] = useState<Map<string, Empresa[]>>(new Map());
```

### 3. Infinite Scroll
Cargar más empresas al hacer scroll en el dropdown:
```typescript
const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
  const bottom = e.currentTarget.scrollHeight - e.currentTarget.scrollTop === e.currentTarget.clientHeight;
  if (bottom && !loading) loadMoreEmpresas();
};
```

### 4. Crear Empresa Rápida
Botón para crear empresa nueva sin salir del formulario:
```tsx
<button onClick={() => setShowCreateModal(true)}>
  + Crear nueva empresa
</button>
```

---

## Testing

### Casos de Prueba:
1. ✅ Abrir dropdown y ver lista de empresas
2. ✅ Buscar empresa por razón social
3. ✅ Buscar empresa por NIT
4. ✅ Seleccionar empresa de la lista
5. ✅ Escribir texto libre (empresa nueva)
6. ✅ Limpiar valor con botón X
7. ✅ Cerrar dropdown al hacer click fuera
8. ✅ Componente deshabilitado
9. ✅ Mostrar mensaje cuando no hay resultados
10. ✅ Mostrar mensaje de límite de 50 empresas

---

## Conclusión

✅ **Implementación exitosa**

Se reemplazó el input de texto libre por un componente de autocompletado inteligente que mejora la experiencia de usuario y la consistencia de datos.

**Impacto:**
- Mejor UX en formularios de impresoras y usuarios
- Datos más consistentes en la base de datos
- Componente reutilizable para futuros formularios

**Próximos pasos:**
- Monitorear uso y feedback de usuarios
- Considerar implementar mejoras futuras si es necesario
- Aplicar patrón similar a otros campos (ej: Centro de Costos)

---

**Preparado por:** Kiro AI Assistant  
**Fecha:** 20 de Marzo de 2026  
**Versión:** 1.0
