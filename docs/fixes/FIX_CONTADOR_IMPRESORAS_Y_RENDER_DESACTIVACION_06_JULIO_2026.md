# Fix: Consistencia en Conteo de Impresoras y Renderizado de Desactivaciones Lógicas (06 de Julio de 2026)

Este documento detalla el diagnóstico, la causa raíz y la solución implementada para corregir la incoherencia visual en la columna de **Impresoras** de la gestión de usuarios, donde las impresoras se renderizaban como `0` en la fila principal pero mostraban asignaciones inactivas al expandir el acordeón.

---

## 1. Descripción del Problema
En el módulo de **Administración de Usuarios** (`/administracion`), cuando un usuario era desactivado en la base de datos o en todas sus impresoras asociadas:
* La fila principal en la tabla de usuarios mostraba **`0`** en la columna de Impresoras (círculo azul).
* Si el administrador hacía clic en el botón de expandir (`>`) para ver el desglose, el círculo azul cambiaba repentinamente de **`0`** a **`1`** (o el número real de impresoras asignadas).
* Esto obligaba al administrador a abrir el detalle de cada usuario para poder ver si realmente tenía o no impresoras asociadas en el historial de base de datos.
* Al desactivar a un usuario en caliente, la columna no se renderizaba correctamente en la fila principal sin forzar la recarga o expansión del acordeón.

---

## 2. Causa Raíz
El error se debía a una inconsistencia entre los endpoints del backend y el estado perezoso (lazy-loading) del frontend:
1. **Filtro del Endpoint General (`/users/`)**: La propiedad `@property def impresoras(self)` del modelo `User` en `backend/db/models.py` filtraba las asignaciones para excluir aquellas que tuvieran `is_active = False` (`if not assoc.is_active: continue`). Por lo tanto, el backend devolvía `impresoras: []` (vacío) en el JSON de consulta general.
2. **Diferencia con el Endpoint de Detalle (`/provisioning/user/{id}`)**: Al hacer clic en expandir, el frontend llamaba a `obtenerUsuarioConEquipos(id)`, el cual consulta el endpoint de aprovisionamiento del backend. Este último devuelve la lista de **todas** las asignaciones (tanto activas como inactivas) registradas en la tabla `user_printer_assignments`.
3. **Estado Inicial del Acordeón**: En `FilaUsuario.tsx`, como la información perezosa no se había cargado, el estado local `equipos` estaba vacío (`[]`), forzando a pintar `0`. Al expandirse, se cargaba la lista completa de asignaciones inactivas y cambiaba dinámicamente a `1` o `2` en el frontend, rompiendo la coherencia de datos.

---

## 3. Solución Implementada

### A. Backend (Consistencia de Datos en Consulta General)
* **Modelo de Base de Datos (`backend/db/models.py`)**: Modificamos la propiedad `@property def impresoras(self)` para no excluir las asignaciones inactivas y agregamos el campo `"is_active": assoc.is_active` en el diccionario serializado.
* **Esquema API (`backend/api/schemas.py`)**: Agregamos el campo `is_active: Optional[bool] = None` a la clase `UserPrinterResponse` para propagar el estado de activación lógica a través de la API.

### B. Frontend (Renderizado Coherente y Reactivo)
* **Tipado de Datos (`src/types/usuario.ts`)**: Añadimos el campo `is_active?: boolean;` a la interfaz `ImpresoraUsuario` y al tipo de `EquipoAsignado` agregamos `permisos?: ...` opcional para prevenir errores de tipado de TypeScript.
* **Fila de Usuario (`src/components/usuarios/FilaUsuario.tsx`)**:
  * **Conteo Unificado**: Modificamos el renderizado de la columna de Impresoras en la fila principal. Ahora clasifica las asignaciones en **activas** e **inactivas** (tanto si se precargan de la API como si se obtienen de forma perezosa):
    * Si el usuario tiene impresoras **activas**, se muestra el círculo azul brillante con el número de impresoras activas.
    * Si tiene impresoras asignadas pero **todas están inactivas/desactivadas**, se muestra el número **`0` en un círculo gris atenuado**, indicando que no tiene acceso activo pero sí historial de asignación.
    * Si no tiene asignaciones, muestra `-`.
  * **Visualización en Detalle**: En el listado de impresoras del desglose expandido, si una impresora está inactiva (`impresora.is_active === false`), la tarjeta se renderiza con un fondo gris (`opacity-60 bg-slate-100/70`) y con un badge rojo de **`Desactivado`** al lado del nombre de la impresora.

---

## 4. Verificación y Despliegue
* **Compilación de Producción**: Se ejecutó `npm run build` en local de forma exitosa (cero errores de TypeScript/Vite).
* **Despliegue**: Se corrió el script `deployment/upload_changes.py` para subir los archivos backend/frontend al servidor de producción y reiniciar los contenedores `ricoh-backend` y `ricoh-frontend`.
* **Prueba en Vivo**: Se verificó el comportamiento abriendo la IP de producción real `192.168.91.131` en el navegador, buscando usuarios inactivos (como AMANDA AVILA, código `1923`) y corroborando que ahora muestran el **`0`** en gris en la fila principal al instante, y que el detalle renderiza las tarjetas con el badge de **`Desactivado`** correctamente.

---

## 5. Módulo de Reportes: Corrección en Reactividad de Filtros Comparativos

### A. Diagnóstico y Causa Raíz
Durante el control de calidad del módulo de **Reportes & Analytics** (`/analytics`), se reportó que al cambiar el **Período Base (Inicial - Más Antiguo)** los datos no variaban y permanecían fijos.
* **Causa**: En `AnalyticsPage.tsx`, los selectores de períodos (A y B) utilizaban el índice de posición en el arreglo (`value={idx}`) como su valor de selección. Cuando se cargaban los períodos dinámicos del servidor (`uniquePeriods`), un efecto `useEffect` forzaba el reinicio de las variables de estado `dateRangeA` y `dateRangeB` a las primeras posiciones por defecto si detectaba un cambio de índice, ignorando la selección manual del usuario.
* **Caché de Redis**: El decorador `@cache_result("analytics:comparison", ttl=3600)` en el backend de FastAPI maneja correctamente claves por parámetros de fechas (`fecha_inicio_a`, `fecha_fin_a`, etc.), por lo que el problema residía netamente en el ciclo de vida del estado de React y la inicialización del selector.

### B. Solución Implementada
1. **Identificadores Estables**: Cambiamos el valor de selección de los desplegables de un índice numérico simple a una clave compuesta de fechas: `value={`${p.start}_${p.end}`}`.
2. **Protección de Selección del Usuario**: Introdujimos flags de estado `userChangedA` y `userChangedB` para rastrear si el usuario ha realizado un cambio manual. El `useEffect` de inicialización dinámica ahora solo aplica los períodos por defecto la primera vez y nunca sobreescribe la selección activa del usuario.
3. **Limpieza de Caché**: Ejecutamos el script `deployment/clear_analytics_cache.py` para purgar las claves antiguas en el Redis de producción y forzar un recálculo limpio de las diferencias de consumo.

### C. Pruebas de Calidad Realizadas (QA)
Se realizaron pruebas de extremo a extremo automatizadas en el navegador directamente en el entorno de producción (`192.168.91.131`):
1. **Fijación de Período a Comparar**: Seleccionamos como período reciente/final el cierre de junio (`19 jun 2026`).
2. **Prueba de Cambio en Período Base**:
   * Cambiamos el período inicial/antiguo a `20 may 2026`: La variación de consumo se actualizó reactivamente a **`+100.88%`**.
   * Cambiamos el período inicial/antiguo a `06 may 2026`: La variación se actualizó instantáneamente a **`+43.99%`**.
   * Cambiamos el período inicial/antiguo a `21 abr 2026`: La variación se actualizó instantáneamente a **`+287.41%`**.
3. **Evidencia Visual**: La captura de pantalla en [analytics_period_21_apr](file:///C:/Users/juan.lizarazo/.gemini/antigravity-ide/brain/a93c5d5f-6268-4ecf-a059-e847279132e4/analytics_period_21_apr_1783362110819.png) evidencia las tarjetas KPI superiores y el gráfico con la selección de abril cargada con total integridad de datos.

