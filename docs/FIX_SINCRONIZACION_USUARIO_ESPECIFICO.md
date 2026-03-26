# Fix: Sincronización de Usuario Específico No Funcionaba

**Fecha**: 25 de marzo de 2026
**Estado**: ✅ RESUELTO
**Problema**: Al especificar un código de usuario en el campo "Especificar usuario" y hacer clic en "Buscar Usuario", el sistema sincronizaba TODOS los usuarios en lugar de solo el usuario especificado.

## Problema Identificado

El componente `AdministracionUsuarios.tsx` tenía un selector para elegir entre:
- "Sincronizar todos" → Sincroniza todos los usuarios de todas las impresoras
- "Especificar usuario" → Debería sincronizar solo el usuario con el código especificado

Sin embargo, el frontend NO estaba enviando el parámetro `user_code` al backend, por lo que siempre sincronizaba todos los usuarios.

### Evidencia en Logs

```
User code: TODOS
```

Aunque el usuario especificó un código en el frontend, el backend recibía `None` y lo interpretaba como "TODOS".

## Causa Raíz

1. El servicio `discoveryService.syncUsersFromPrinters()` NO aceptaba parámetros
2. El componente `AdministracionUsuarios.tsx` NO enviaba el código de usuario al servicio
3. El endpoint del backend SÍ aceptaba el parámetro `user_code` pero era opcional con valor por defecto `None`

### Código Anterior (INCORRECTO)

**discoveryService.ts:**
```typescript
syncUsersFromPrinters: async (): Promise<{ ... }> => {
  const response = await apiClient.post('/discovery/sync-users-from-printers');
  return response.data;
}
```

**AdministracionUsuarios.tsx:**
```typescript
const handleSincronizar = async () => {
  const response = await discoveryService.syncUsersFromPrinters();
  // No enviaba el código de usuario
}
```

## Solución Implementada

### 1. Modificado el Servicio para Aceptar Parámetro

**src/services/discoveryService.ts:**
```typescript
syncUsersFromPrinters: async (userCode?: string): Promise<{ 
  success: boolean; 
  message: string;
  users?: any[];
  printers_scanned?: any[];
  total_usuarios_unicos?: number;
  usuarios_en_db?: number;
  usuarios_solo_impresoras?: number;
  search_mode?: string;
  user_code_searched?: string;
}> => {
  const params = userCode ? { user_code: userCode } : {};
  const response = await apiClient.post('/discovery/sync-users-from-printers', null, { params });
  return response.data;
}
```

### 2. Modificado el Componente para Enviar el Código

**src/components/usuarios/AdministracionUsuarios.tsx:**
```typescript
const handleSincronizar = async () => {
  try {
    setSincronizando(true);

    // Determinar si se debe buscar un usuario específico
    const userCode = modoSincronizacion === 'especifico' && codigoUsuarioBuscar.trim() 
      ? codigoUsuarioBuscar.trim() 
      : undefined;

    console.log('🔍 Sincronizando con parámetros:', { 
      modo: modoSincronizacion, 
      userCode 
    });

    const response = await discoveryService.syncUsersFromPrinters(userCode);
    
    // ... resto del código
  }
}
```

## Comportamiento Esperado

### Caso 1: Sincronizar Todos ✅
- Usuario selecciona: "Sincronizar todos"
- Parámetro enviado: `undefined` (sin user_code)
- Backend recibe: `user_code=None`
- Logs: `User code: TODOS`
- Resultado: Sincroniza todos los usuarios de todas las impresoras

### Caso 2: Especificar Usuario ✅
- Usuario selecciona: "Especificar usuario"
- Usuario ingresa: "j1254" en el campo
- Parámetro enviado: `user_code=j1254`
- Backend recibe: `user_code=j1254`
- Logs: `User code: j1254`
- Resultado: Solo sincroniza el usuario con código "j1254"

## Archivos Modificados

- `src/services/discoveryService.ts`
  - Agregado parámetro opcional `userCode` a `syncUsersFromPrinters`
  - Agregados campos de respuesta `search_mode` y `user_code_searched`

- `src/components/usuarios/AdministracionUsuarios.tsx`
  - Modificada función `handleSincronizar` para enviar el código de usuario cuando esté en modo "específico"
  - Agregado log de debug para verificar parámetros enviados

## Pruebas Realizadas

✅ Sincronizar todos los usuarios → Funciona correctamente
✅ Especificar código de usuario → Solo sincroniza ese usuario
✅ Campo vacío en modo específico → Botón deshabilitado (validación existente)

## Notas Técnicas

- El parámetro se envía como query parameter en la URL: `/discovery/sync-users-from-printers?user_code=j1254`
- El backend ya tenía la lógica implementada, solo faltaba que el frontend enviara el parámetro
- La validación del botón (deshabilitado cuando el campo está vacío) ya existía y sigue funcionando
