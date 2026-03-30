# Guía de Uso de Sileo

**Fecha**: 30 de Marzo de 2026  
**Versión**: 1.0.0

---

## Introducción

Sileo es una librería de notificaciones toast para React que utiliza animaciones basadas en física (spring physics) y efectos de morphing SVG para crear notificaciones visualmente atractivas y fluidas.

---

## Instalación

```bash
npm install sileo
```

---

## Configuración Básica

### 1. Importar y Configurar el Toaster

En tu archivo raíz (ej: `src/App.tsx`):

```tsx
import { Toaster } from 'sileo';
import 'sileo/styles.css';

function App() {
  return (
    <>
      <Toaster 
        position="top-center"
        offset={20}
        options={{
          duration: 4000,
          autopilot: true
        }}
        theme="system"
      />
      <YourApp />
    </>
  );
}
```

### 2. Crear el Hook Personalizado

Archivo: `src/hooks/useNotification.ts`

```typescript
import { sileo } from 'sileo';

export const useNotification = () => {
  return {
    success: (message: string, description?: string) => {
      sileo.success({ title: message, description });
    },
    
    error: (message: string, description?: string) => {
      sileo.error({ title: message, description });
    },
    
    info: (message: string, description?: string) => {
      sileo.info({ title: message, description });
    },
    
    warning: (message: string, description?: string) => {
      sileo.warning({ title: message, description });
    },
    
    loading: (message: string, description?: string) => {
      return sileo.show({ 
        title: message, 
        description,
        state: 'loading'
      });
    },
    
    promise: <T,>(
      promise: Promise<T>,
      messages: {
        loading: string;
        success: string | ((data: T) => string);
        error: string | ((error: any) => string);
      }
    ) => {
      return sileo.promise(promise, {
        loading: { title: messages.loading },
        success: (data) => ({
          title: typeof messages.success === 'function' 
            ? messages.success(data) 
            : messages.success
        }),
        error: (err) => ({
          title: typeof messages.error === 'function' 
            ? messages.error(err) 
            : messages.error
        })
      });
    },
  };
};
```

---

## Uso en Componentes

### Importar el Hook

```tsx
import { useNotification } from '@/hooks/useNotification';

function MyComponent() {
  const notify = useNotification();
  
  // Usar las notificaciones...
}
```

### Ejemplos de Uso

#### 1. Notificación de Éxito

```tsx
const handleSave = async () => {
  try {
    await saveData();
    notify.success('Datos guardados', 'Los cambios se guardaron correctamente');
  } catch (error) {
    notify.error('Error al guardar', 'No se pudieron guardar los cambios');
  }
};
```

#### 2. Notificación de Error

```tsx
const handleDelete = async () => {
  try {
    await deleteItem();
    notify.success('Elemento eliminado', 'El elemento se eliminó correctamente');
  } catch (error: any) {
    notify.error('Error al eliminar', error.message || 'No se pudo eliminar el elemento');
  }
};
```

#### 3. Notificación de Advertencia

```tsx
const handleValidation = () => {
  if (!formData.email) {
    notify.warning('Campo requerido', 'Debes ingresar un correo electrónico');
    return;
  }
  // Continuar...
};
```

#### 4. Notificación de Información

```tsx
const showInfo = () => {
  notify.info('Actualización disponible', 'Hay una nueva versión del sistema disponible');
};
```

#### 5. Notificación con Promesa

```tsx
const handleUpload = async () => {
  const uploadPromise = uploadFile(file);
  
  await notify.promise(uploadPromise, {
    loading: 'Subiendo archivo...',
    success: 'Archivo subido correctamente',
    error: 'Error al subir el archivo'
  });
};
```

#### 6. Notificación con Promesa y Datos Dinámicos

```tsx
const handleFetch = async () => {
  const fetchPromise = fetchData();
  
  await notify.promise(fetchPromise, {
    loading: 'Cargando datos...',
    success: (data) => `Se cargaron ${data.length} registros`,
    error: (err) => `Error: ${err.message}`
  });
};
```

---

## Opciones de Configuración

### Posiciones Disponibles

```typescript
type SileoPosition = 
  | 'top-left' 
  | 'top-center' 
  | 'top-right' 
  | 'bottom-left' 
  | 'bottom-center' 
  | 'bottom-right';
```

### Opciones del Toaster

```tsx
<Toaster 
  position="top-center"           // Posición de los toasts
  offset={20}                     // Offset desde los bordes (px)
  options={{
    duration: 4000,               // Duración en ms (null = infinito)
    autopilot: true,              // Animaciones automáticas
    roundness: 12,                // Radio de borde en px
  }}
  theme="system"                  // "light" | "dark" | "system"
/>
```

### Opciones por Toast Individual

```tsx
sileo.success({
  title: 'Título',
  description: 'Descripción opcional',
  duration: 5000,                 // Duración específica
  position: 'bottom-right',       // Posición específica
  icon: <CustomIcon />,           // Icono personalizado
});
```

---

## Mejores Prácticas

### 1. Mensajes Claros y Concisos

✅ **Bueno**:
```tsx
notify.success('Archivo descargado', 'El archivo Excel se descargó correctamente');
```

❌ **Malo**:
```tsx
notify.success('Éxito', 'Operación completada');
```

### 2. Descripciones Útiles

✅ **Bueno**:
```tsx
notify.error('Error de conexión', 'No se pudo conectar con el servidor. Verifica tu conexión a internet');
```

❌ **Malo**:
```tsx
notify.error('Error', 'Algo salió mal');
```

### 3. Mensajes en Español Natural

✅ **Bueno**:
```tsx
notify.warning('Selecciona una opción', 'Debes seleccionar al menos un elemento');
```

❌ **Malo**:
```tsx
notify.warning('Selección requerida', 'Por favor seleccione un elemento');
```

### 4. Consistencia en Formato

Siempre usar el formato: **Título corto** + **Descripción detallada**

```tsx
notify.success(
  'Acción completada',           // Título: Qué pasó
  'Descripción del resultado'    // Descripción: Detalles adicionales
);
```

### 5. Manejo de Errores

```tsx
try {
  await operation();
  notify.success('Operación exitosa', 'Los datos se procesaron correctamente');
} catch (error: any) {
  const message = error.response?.data?.message || error.message || 'Error desconocido';
  notify.error('Error en la operación', message);
}
```

---

## Características Avanzadas

### 1. Notificaciones con Botones de Acción

```tsx
sileo.action({
  title: 'Elemento eliminado',
  description: '¿Deseas deshacer esta acción?',
  button: {
    title: 'Deshacer',
    onClick: () => {
      // Lógica para deshacer
      restoreItem();
    }
  }
});
```

### 2. Notificaciones Persistentes

```tsx
// No se cierra automáticamente
const toastId = sileo.show({
  title: 'Procesando...',
  description: 'Esta operación puede tardar varios minutos',
  duration: null  // null = no se cierra automáticamente
});

// Cerrar manualmente después
sileo.dismiss(toastId);
```

### 3. Limpiar Todas las Notificaciones

```tsx
// Limpiar todas las notificaciones
sileo.clear();

// Limpiar notificaciones de una posición específica
sileo.clear('top-center');
```

---

## Estilos y Temas

### Tema Automático

Sileo se adapta automáticamente al tema del sistema:

```tsx
<Toaster theme="system" />  // Recomendado
```

### Tema Forzado

```tsx
<Toaster theme="light" />   // Siempre claro
<Toaster theme="dark" />    // Siempre oscuro
```

### Personalización de Estilos

```tsx
sileo.success({
  title: 'Éxito',
  styles: {
    title: { color: '#10b981' },
    description: { fontSize: '14px' },
    badge: { backgroundColor: '#10b981' }
  }
});
```

---

## Troubleshooting

### Problema: Los toasts no aparecen

**Solución**: Verifica que hayas importado los estilos:
```tsx
import 'sileo/styles.css';
```

### Problema: Los toasts tapan otros elementos

**Solución**: Ajusta el `offset` o cambia la `position`:
```tsx
<Toaster position="top-center" offset={20} />
```

### Problema: Los toasts desaparecen muy rápido

**Solución**: Aumenta la duración:
```tsx
<Toaster options={{ duration: 5000 }} />
```

---

## Recursos

- [Documentación Oficial](https://sileo.aaryan.design)
- [GitHub Repository](https://github.com/hiaaryan/sileo)
- [Playground Interactivo](https://sileo.aaryan.design/playground)

---

**Versión de Sileo**: 0.1.5  
**Última actualización**: 30 de Marzo de 2026
