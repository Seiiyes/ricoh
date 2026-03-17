# 📚 Lecciones Aprendidas - Sistema de Retroalimentación

Esta carpeta contiene documentación de errores cometidos durante el desarrollo, sus causas raíz y soluciones implementadas. El objetivo es crear un sistema de aprendizaje continuo para evitar repetir los mismos errores.

---

## 📋 Índice de Lecciones

### Errores de Backend
1. [Error de Importación en API](./001-error-importacion-api.md) - `counters.py` no importaba `counter_schemas`
2. [Consumo de Usuarios en Cero](./002-consumo-usuarios-cero.md) - Lógica incorrecta en primer cierre
3. [Conflicto de Rutas en FastAPI](./003-conflicto-rutas-fastapi.md) - Rutas ambiguas en endpoints
6. [Comparación Usando Campo Incorrecto](./006-comparacion-campo-incorrecto.md) - Usaba `total_paginas` en lugar de `consumo_total`
8. [Cierre Sin Filtrar Lecturas Por Fecha](./008-cierre-sin-filtrar-por-fecha.md) - No filtraba contadores por fecha del cierre

### Errores de Frontend
4. [Ruta Incorrecta de API](./004-ruta-incorrecta-api.md) - Frontend usaba `/api/printers` en lugar de `/printers`

### Errores de Base de Datos
5. [Falta de Datos de Usuarios](./005-falta-datos-usuarios.md) - No hay lecturas de usuarios para ciertos días

### Errores de Infraestructura
7. [Backend Unhealthy Durante Inicio de PostgreSQL](./007-backend-unhealthy-postgres-startup.md) - Backend falla al iniciar porque PostgreSQL está arrancando

---

## 🎯 Cómo Usar Este Sistema

### Para Documentar un Nuevo Error
1. Crear archivo: `.kiro/lessons-learned/XXX-nombre-descriptivo.md`
2. Usar la plantilla proporcionada
3. Actualizar este README con el enlace
4. Agregar tags para búsqueda rápida

### Para Consultar Antes de Implementar
1. Buscar por palabra clave en este README
2. Leer lecciones relacionadas
3. Aplicar las mejores prácticas documentadas

### Para Revisar Periódicamente
- Revisar mensualmente las lecciones más recientes
- Identificar patrones de errores recurrentes
- Actualizar guías de desarrollo

---

## 📊 Estadísticas

- **Total de lecciones:** 8
- **Errores de backend:** 5
- **Errores de frontend:** 1
- **Errores de base de datos:** 1
- **Errores de infraestructura:** 1
- **Última actualización:** 9 de marzo de 2026

---

## 🏷️ Tags para Búsqueda

- `#importacion` - Errores de importación de módulos
- `#logica-negocio` - Errores en lógica de negocio
- `#comparacion` - Errores en comparaciones
- `#campos` - Uso incorrecto de campos de base de datos
- `#api` - Errores en endpoints REST
- `#frontend` - Errores en componentes React
- `#base-datos` - Errores relacionados con datos
- `#validacion` - Errores de validación
- `#performance` - Problemas de rendimiento
- `#seguridad` - Problemas de seguridad

---

## 📝 Plantilla para Nuevas Lecciones

```markdown
# [Número] - [Título Descriptivo]

**Fecha:** [Fecha del error]  
**Severidad:** [Crítica/Alta/Media/Baja]  
**Módulo:** [Backend/Frontend/Base de Datos/Infraestructura]  
**Tags:** #tag1 #tag2 #tag3

---

## 🐛 Descripción del Error

[Descripción clara del error que ocurrió]

## 🔍 Síntomas

- Síntoma 1
- Síntoma 2
- Síntoma 3

## 🎯 Causa Raíz

[Explicación de por qué ocurrió el error]

## ✅ Solución Implementada

[Descripción de la solución]

### Código Antes
\`\`\`python
# Código incorrecto
\`\`\`

### Código Después
\`\`\`python
# Código corregido
\`\`\`

## 🛡️ Prevención Futura

- [ ] Acción preventiva 1
- [ ] Acción preventiva 2
- [ ] Acción preventiva 3

## 📚 Referencias

- [Documento relacionado 1]
- [Documento relacionado 2]

## 💡 Lecciones Clave

1. Lección 1
2. Lección 2
3. Lección 3

---

**Documentado por:** [Nombre]  
**Revisado por:** [Nombre]  
**Estado:** [Resuelto/En progreso/Pendiente]
```

---

## 🔄 Proceso de Revisión

### Semanal
- Revisar nuevas lecciones agregadas
- Verificar que las soluciones funcionan
- Actualizar estadísticas

### Mensual
- Identificar patrones de errores
- Actualizar guías de desarrollo
- Compartir lecciones con el equipo

### Trimestral
- Análisis de tendencias
- Actualizar procesos de desarrollo
- Capacitación basada en lecciones

---

**Última actualización:** 4 de marzo de 2026  
**Mantenido por:** Sistema Kiro
