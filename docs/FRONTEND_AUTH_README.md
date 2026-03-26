# Frontend - Sistema de Autenticación

## 📋 Estado de Implementación

✅ **Fase 6 completada**: Autenticación Frontend (Tareas 36-43)
✅ **Fase 7 completada**: Gestión de Empresas y Usuarios Admin (Tareas 44-52)

### Archivos Creados - Fase 6

1. `src/services/apiClient.ts` - Cliente API con interceptores
2. `src/services/authService.ts` - Servicio de autenticación
3. `src/contexts/AuthContext.tsx` - Contexto de autenticación
4. `src/components/ProtectedRoute.tsx` - Componente de rutas protegidas
5. `src/pages/LoginPage.tsx` - Página de login
6. `src/pages/UnauthorizedPage.tsx` - Página de acceso denegado
7. `src/pages/Dashboard.tsx` - Dashboard principal con sidebar
8. `src/App.tsx` - Actualizado con rutas y AuthProvider

### Archivos Creados - Fase 7

1. `src/services/empresaService.ts` - Servicio de empresas
2. `src/services/adminUserService.ts` - Servicio de usuarios admin
3. `src/components/EmpresaModal.tsx` - Modal para crear/editar empresas
4. `src/components/AdminUserModal.tsx` - Modal para crear/editar usuarios admin
5. `src/pages/EmpresasPage.tsx` - Página de gestión de empresas
6. `src/pages/AdminUsersPage.tsx` - Página de gestión de usuarios admin
7. `src/pages/Dashboard.tsx` - Actualizado con rutas reales

## 🚀 Instalación

### 1. Instalar React Router

```bash
npm install react-router-dom
```

### 2. Configurar Variables de Entorno

Crear archivo `.env.local` en la raíz del proyecto:

```bash
VITE_API_URL=http://localhost:8000
```

### 3. Iniciar el Servidor de Desarrollo

```bash
npm run dev
```

## 🔐 Credenciales de Prueba

```
Usuario: superadmin
Contraseña: {:Z75M!=x>9PiPp2
```

## ✨ Funcionalidades Implementadas

### Fase 6: Autenticación
- ✅ Login con validación de formulario
- ✅ Manejo de errores (credenciales inválidas, cuenta bloqueada, etc.)
- ✅ Almacenamiento de tokens en localStorage
- ✅ Renovación automática de token cada 25 minutos
- ✅ Logout con limpieza de sesión
- ✅ Interceptores de axios para agregar token automáticamente
- ✅ Rutas protegidas con validación de roles
- ✅ Dashboard con sidebar y navegación

### Fase 7: Gestión de Empresas y Usuarios Admin
- ✅ Gestión completa de empresas (CRUD)
  - Crear, editar y desactivar empresas
  - Búsqueda por razón social o nombre comercial
  - Paginación (20 empresas por página)
  - Validación de campos (formato kebab-case, email, etc.)
  - Manejo de duplicados
- ✅ Gestión completa de usuarios admin (CRUD)
  - Crear, editar y desactivar usuarios admin
  - Búsqueda por username, nombre o email
  - Filtros por rol y empresa
  - Paginación (20 usuarios por página)
  - Validación de contraseña con medidor de fortaleza
  - Validación de empresa según rol
- ✅ Navbar con información del usuario
  - Avatar con iniciales
  - Badge de rol con colores
  - Información de empresa (si aplica)
  - Dropdown con logout
- ✅ Control de acceso basado en roles
  - Solo superadmin puede acceder a /empresas y /admin-users
  - Redirección automática a /unauthorized si no tiene permisos

### Rutas
- ✅ Rutas públicas: `/login`, `/unauthorized`
- ✅ Rutas protegidas: Todas las demás requieren autenticación
- ✅ Rutas con roles: `/empresas` y `/admin-users` solo para superadmin
- ✅ Redirección automática a login si no está autenticado
- ✅ Redirección a unauthorized si no tiene permisos

### UI/UX
- ✅ Diseño moderno y consistente
- ✅ Loading states durante operaciones
- ✅ Mensajes de error descriptivos
- ✅ Confirmaciones antes de eliminar
- ✅ Indicadores visuales de estado (activo/inactivo)
- ✅ Badges de rol con colores
- ✅ Responsive design

## 📝 Próximos Pasos

El sistema está completamente funcional. Próximas mejoras opcionales:
- [ ] Tests unitarios para componentes de frontend
- [ ] Funcionalidad de cambio de contraseña desde el perfil
- [ ] Página de perfil de usuario
- [ ] Exportación de datos a Excel/CSV
- [ ] Gráficos y estadísticas

## 🧪 Testing

Para probar el sistema:

1. Iniciar el backend:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. Iniciar el frontend:
   ```bash
   npm run dev
   ```

3. Abrir http://localhost:5173

4. Login con superadmin

5. Verificar:
   - Login exitoso redirige al dashboard
   - Token se guarda en localStorage
   - Sidebar muestra información del usuario
   - Opciones de "Gestión de Empresas" y "Usuarios Admin" visibles
   - Crear, editar y desactivar empresas funciona
   - Crear, editar y desactivar usuarios admin funciona
   - Validaciones funcionan correctamente
   - Búsqueda y filtros funcionan
   - Paginación funciona
   - Logout limpia sesión y redirige a login

## 🔧 Troubleshooting

### Error: "Cannot find module 'react-router-dom'"
**Solución**: Instalar React Router
```bash
npm install react-router-dom
```

### Error: "VITE_API_URL is not defined"
**Solución**: Crear archivo `.env.local` con:
```
VITE_API_URL=http://localhost:8000
```

### Error 401 en todas las peticiones
**Solución**: Verificar que el backend está corriendo en http://localhost:8000

### Login no funciona
**Solución**: 
1. Verificar que el backend está corriendo
2. Verificar credenciales (superadmin / {:Z75M!=x>9PiPp2)
3. Revisar consola del navegador para errores

### No puedo acceder a /empresas o /admin-users
**Solución**: Solo el superadmin puede acceder a estas rutas. Verificar que estás logueado como superadmin.

## 📚 Documentación

- **Backend API**: http://localhost:8000/docs
- **Guía de Usuario**: `docs/GUIA_USUARIO.md`
- **Guía Rápida**: `docs/GUIA_RAPIDA.md`
- **Sistema Completado**: `docs/SISTEMA_AUTENTICACION_COMPLETADO.md`

---

**Implementado**: 20 de Marzo de 2026  
**Estado**: Fases 6 y 7 completadas - Sistema completamente funcional
