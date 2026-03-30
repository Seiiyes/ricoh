# 📝 Flujo de Trabajo con Git

## 🔧 Configuración Inicial (Ya Completada)

```bash
git init
git remote add origin https://github.com/Seiiyes/ricoh.git
git config user.name "Juan Lizarazo"
git config user.email "juan.lizarazo@reliteltda.com"
```

---

## 📤 Subir Cambios al Repositorio

### 1. Ver Estado de los Archivos

```bash
git status
```

Esto muestra:
- Archivos modificados (en rojo)
- Archivos en staging (en verde)
- Archivos sin seguimiento

### 2. Agregar Archivos al Staging

**Agregar todos los archivos:**
```bash
git add .
```

**Agregar archivos específicos:**
```bash
git add archivo1.py archivo2.tsx
```

**Agregar por carpeta:**
```bash
git add backend/
git add src/components/
```

### 3. Hacer Commit

**Commit con mensaje descriptivo:**
```bash
git commit -m "feat: descripción del cambio"
```

**Tipos de commits (Conventional Commits):**
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios en documentación
- `style:` - Cambios de formato (no afectan código)
- `refactor:` - Refactorización de código
- `test:` - Agregar o modificar tests
- `chore:` - Tareas de mantenimiento

**Ejemplos:**
```bash
git commit -m "feat: agregar reintentos automáticos"
git commit -m "fix: corregir error de índice autoincremental"
git commit -m "docs: actualizar README con nueva versión"
git commit -m "refactor: mejorar estructura de servicios"
```

### 4. Subir al Repositorio

**Primera vez (ya hecho):**
```bash
git push -u origin main
```

**Siguientes veces:**
```bash
git push
```

---

## 🔄 Flujo Completo (Resumen)

```bash
# 1. Ver qué cambió
git status

# 2. Agregar cambios
git add .

# 3. Hacer commit
git commit -m "feat: descripción del cambio"

# 4. Subir a GitHub
git push
```

---

## 📋 Comandos Útiles

### Ver Historial de Commits

```bash
git log
git log --oneline  # Versión compacta
```

### Ver Diferencias

```bash
git diff  # Ver cambios no agregados
git diff --staged  # Ver cambios en staging
```

### Deshacer Cambios

**Deshacer cambios en un archivo (antes de add):**
```bash
git checkout -- archivo.py
```

**Quitar archivo del staging (después de add):**
```bash
git reset HEAD archivo.py
```

**Deshacer último commit (mantiene cambios):**
```bash
git reset --soft HEAD~1
```

### Ver Archivos Ignorados

```bash
git status --ignored
```

---

## 🌿 Trabajar con Ramas

### Crear Nueva Rama

```bash
git checkout -b feature/nueva-funcionalidad
```

### Cambiar de Rama

```bash
git checkout main
git checkout feature/nueva-funcionalidad
```

### Ver Ramas

```bash
git branch  # Ramas locales
git branch -a  # Todas las ramas
```

### Fusionar Rama

```bash
git checkout main
git merge feature/nueva-funcionalidad
```

### Subir Rama al Repositorio

```bash
git push -u origin feature/nueva-funcionalidad
```

---

## 🔍 Verificar Estado del Repositorio

### Ver Configuración

```bash
git config --list
```

### Ver Remoto

```bash
git remote -v
```

### Ver Último Commit

```bash
git show
```

---

## 📦 Escenarios Comunes

### Escenario 1: Modificaste Varios Archivos

```bash
# Ver qué cambió
git status

# Agregar todos los cambios
git add .

# Commit con mensaje descriptivo
git commit -m "feat: mejoras en el sistema de aprovisionamiento"

# Subir
git push
```

### Escenario 2: Solo Modificaste Documentación

```bash
git add *.md
git commit -m "docs: actualizar documentación"
git push
```

### Escenario 3: Corrección de Bug

```bash
git add backend/services/ricoh_web_client.py
git commit -m "fix: corregir error de timeout en cliente Ricoh"
git push
```

### Escenario 4: Nueva Funcionalidad Grande

```bash
# Crear rama para la funcionalidad
git checkout -b feature/notificaciones-email

# Hacer cambios...
git add .
git commit -m "feat: agregar sistema de notificaciones por email"

# Subir rama
git push -u origin feature/notificaciones-email

# Cuando esté lista, fusionar con main
git checkout main
git merge feature/notificaciones-email
git push
```

---

## 🚨 Solución de Problemas

### Error: "Your branch is behind"

```bash
# Descargar cambios del repositorio
git pull

# Si hay conflictos, resolverlos manualmente
# Luego hacer commit y push
git add .
git commit -m "merge: resolver conflictos"
git push
```

### Error: "Authentication failed"

```bash
# Verificar credenciales
# GitHub pedirá autenticación en el navegador
git push
```

### Error: "Merge conflict"

```bash
# Ver archivos con conflicto
git status

# Editar archivos manualmente
# Buscar marcadores: <<<<<<< HEAD, =======, >>>>>>>

# Después de resolver
git add .
git commit -m "merge: resolver conflictos"
git push
```

---

## 📝 Buenas Prácticas

1. **Commits frecuentes:** Haz commits pequeños y frecuentes
2. **Mensajes descriptivos:** Usa mensajes claros y concisos
3. **Revisar antes de commit:** Usa `git status` y `git diff`
4. **No subir archivos sensibles:** Verifica el `.gitignore`
5. **Probar antes de push:** Asegúrate de que el código funciona
6. **Usar ramas:** Para funcionalidades grandes, usa ramas

---

## 🔐 Archivos que NO se Suben (en .gitignore)

- `node_modules/` - Dependencias de Node.js
- `__pycache__/` - Cache de Python
- `.env` - Variables de entorno
- `backend/.env` - Variables de entorno del backend
- `*.db` - Bases de datos locales
- `postgres_data/` - Datos de PostgreSQL
- `*.html` (en backend) - Archivos de debug

---

## 📊 Estado Actual del Repositorio

**URL:** https://github.com/Seiiyes/ricoh.git  
**Rama principal:** main  
**Último commit:** docs: Agregar README para GitHub con badges y estructura mejorada  
**Archivos subidos:** 101 archivos  
**Tamaño:** ~191 KB

---

## 🎯 Próximos Pasos

Cuando hagas cambios en el futuro:

1. Abre la terminal en la carpeta del proyecto
2. Ejecuta: `git status` para ver cambios
3. Ejecuta: `git add .` para agregar todos los cambios
4. Ejecuta: `git commit -m "tipo: descripción"` para hacer commit
5. Ejecuta: `git push` para subir a GitHub

---

**Última actualización:** 16 de Febrero de 2026
