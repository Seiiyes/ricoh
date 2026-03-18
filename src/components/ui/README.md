# UI Components

Sistema de componentes reutilizables para garantizar consistencia visual en toda la aplicación.

**Estado:** ✅ Completo (10/10 componentes)  
**Última actualización:** 18 de marzo de 2026

## Componentes Disponibles

✅ Button - Botones con variantes  
✅ Input - Campos de entrada  
✅ Badge - Etiquetas de estado  
✅ Alert - Mensajes de alerta  
✅ Spinner - Indicadores de carga  
✅ Breadcrumbs - Navegación de migas  
✅ Card - Tarjetas base  
✅ Modal - Modales con overlay  
✅ Table - Tablas con sorting/paginación  
✅ Tabs - Pestañas de navegación

### Button
Botón con múltiples variantes y tamaños.

```tsx
import { Button } from '@/components/ui';

<Button variant="primary" size="md">
  Crear Usuario
</Button>

<Button variant="secondary" loading>
  Cargando...
</Button>

<Button variant="danger" icon={<Trash size={16} />}>
  Eliminar
</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
- `size`: 'sm' | 'md' | 'lg'
- `loading`: boolean
- `icon`: ReactNode

### Input
Campo de entrada con label, error y helper text.

```tsx
import { Input } from '@/components/ui';

<Input 
  label="Nombre de Usuario"
  placeholder="Ingresa el nombre"
  helperText="Mínimo 3 caracteres"
/>

<Input 
  label="Código"
  error="Código inválido"
  variant="underline"
/>
```

**Props:**
- `label`: string
- `error`: string
- `helperText`: string
- `variant`: 'default' | 'underline'

### Badge
Etiqueta para mostrar estados o categorías.

```tsx
import { Badge } from '@/components/ui';

<Badge variant="success">Activo</Badge>
<Badge variant="warning">Pendiente</Badge>
<Badge variant="error">Error</Badge>
```

**Props:**
- `variant`: 'success' | 'warning' | 'error' | 'info' | 'neutral'
- `size`: 'sm' | 'md' | 'lg'

### Alert
Mensaje de alerta con icono y opción de cierre.

```tsx
import { Alert } from '@/components/ui';

<Alert variant="success" title="Éxito">
  Usuario creado correctamente
</Alert>

<Alert variant="error" onClose={() => {}}>
  Error al procesar la solicitud
</Alert>
```

**Props:**
- `variant`: 'success' | 'warning' | 'error' | 'info'
- `title`: string
- `onClose`: () => void

### Spinner
Indicador de carga.

```tsx
import { Spinner } from '@/components/ui';

<Spinner size="md" text="Cargando..." />
```

**Props:**
- `size`: 'sm' | 'md' | 'lg' | 'xl'
- `text`: string

### Breadcrumbs
Navegación de migas de pan.

```tsx
import { Breadcrumbs } from '@/components/ui';

<Breadcrumbs 
  items={[
    { label: 'Contadores', onClick: () => navigate('/contadores') },
    { label: 'Cierres', onClick: () => navigate('/cierres') },
    { label: 'Comparación' }
  ]}
/>
```

**Props:**
- `items`: Array<{ label: string, onClick?: () => void }>

### Modal
Modal con overlay, animaciones y cierre automático.

```tsx
import { Modal } from '@/components/ui';

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Editar Usuario"
  size="lg"
>
  <p>Contenido del modal</p>
</Modal>
```

**Props:**
- `isOpen`: boolean
- `onClose`: () => void
- `title`: string (opcional)
- `size`: 'sm' | 'md' | 'lg' | 'xl' | 'full'
- `showCloseButton`: boolean (default: true)
- `closeOnOverlayClick`: boolean (default: true)
- `closeOnEscape`: boolean (default: true)

### Table
Tabla con sorting, paginación y búsqueda.

```tsx
import { Table } from '@/components/ui';

<Table
  columns={[
    { key: 'name', label: 'Nombre', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'status', label: 'Estado', render: (value) => <Badge>{value}</Badge> }
  ]}
  data={users}
  keyExtractor={(row) => row.id}
  sortable
  searchable
  pagination
  pageSize={20}
  onRowClick={(row) => console.log(row)}
/>
```

**Props:**
- `columns`: Array<Column<T>>
- `data`: T[]
- `keyExtractor`: (row: T) => string | number
- `sortable`: boolean (default: true)
- `searchable`: boolean (default: false)
- `pagination`: boolean (default: false)
- `pageSize`: number (default: 10)
- `onRowClick`: (row: T) => void (opcional)

### Tabs
Pestañas con indicador visual y soporte para iconos.

```tsx
import { Tabs } from '@/components/ui';

<Tabs
  tabs={[
    { id: 'resumen', label: 'Resumen', icon: <BarChart size={16} /> },
    { id: 'cierres', label: 'Cierres', icon: <Calendar size={16} /> }
  ]}
  activeTab={activeTab}
  onChange={setActiveTab}
  variant="underline"
/>
```

**Props:**
- `tabs`: Array<{ id: string, label: string, icon?: ReactNode, disabled?: boolean }>
- `activeTab`: string
- `onChange`: (tabId: string) => void
- `variant`: 'default' | 'pills' | 'underline' (default: 'underline')
- `size`: 'sm' | 'md' | 'lg'

## Tokens de Diseño

Los componentes usan tokens de diseño definidos en `src/styles/tokens.ts`:

```typescript
import { colors, spacing, typography } from '@/styles/tokens';
```

## Uso

Todos los componentes se pueden importar desde el index:

```typescript
import { 
  Button, 
  Input, 
  Badge, 
  Alert, 
  Spinner, 
  Breadcrumbs,
  Card,
  Modal,
  Table,
  Tabs
} from '@/components/ui';
```

## Personalización

Los componentes aceptan la prop `className` para personalización adicional:

```tsx
<Button className="w-full mt-4">
  Botón de ancho completo
</Button>
```
