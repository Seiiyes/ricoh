#  Historias de Usuario y Criterios de Aceptación (QA)

Este documento actúa como puente entre los requisitos de negocio y la implementación técnica de la suite **Ricoh Equipment Manager**, definiendo los casos de uso principales, historias de usuario e hitos de aprobación requeridos por control de calidad (QA).

---

##  1. Módulo: Governance (Aprovisionamiento y Control de Usuarios)

### Historia de Usuario 1: Activación Lógica Preservando entry_index
> **Como** Administrador del Sistema,  
> **Quiero** desactivar la asignación de un usuario en un equipo Ricoh en lugar de borrarlo físicamente de la base de datos y de la impresora,  
> **Para** que el usuario conserve su identificador físico (`entry_index`) en el dispositivo y evitar colisiones cuando vuelva a ser enrolado en el futuro.

#### Criterios de Aceptación (QA)
1.  Al hacer clic en "Desactivar" en la interfaz de administración, el flag `is_active` de la asignación debe cambiar a `False` en la base de datos.
2.  La impresora física Ricoh no debe borrar al usuario de su libreta de direcciones, pero se deben deshabilitar temporalmente sus permisos de impresión a color y copias.
3.  Si el usuario vuelve a activarse en la misma impresora, el sistema debe reactivar el registro utilizando el mismo `entry_index` anterior sin generar una nueva posición en la libreta.
4.  Si un escaneo de descubrimiento detecta que un usuario inactivo tiene permisos activos físicamente, el backend debe reactivarlo automáticamente en la base de datos (detección de deriva / drift).

---

##  2. Módulo: Lectura de Contadores y Cierres Mensuales

### Historia de Usuario 2: Eliminación de Cierres Mensuales Equivocados
> **Como** Administrador de Contabilidad y Facturación,  
> **Quiero** poder eliminar un cierre mensual de contadores que contiene lecturas incorrectas o fechas equivocadas,  
> **Para** poder relanzar la lectura de contadores y generar un reporte de cierres limpio.

#### Criterios de Aceptación (QA)
1.  **Seguridad (Multi-tenancy)**: Un administrador solo puede eliminar cierres pertenecientes a impresoras asignadas a su propia empresa. Intentar borrar cierres de otra empresa debe retornar código `HTTP 403 Forbidden`.
2.  **Integridad de Datos**: Al eliminar el cierre mensual principal (`CierreMensual`), se deben borrar en cascada todos los snapshots de consumos por usuario vinculados (`CierreMensualUsuario`) en la base de datos.
3.  **UI/UX Limpia**: Las tarjetas del Historial de Cierres no deben mostrar campos técnicos (como el `ID` de base de datos) y deben contar con un botón papelera con modal de confirmación de **Acción Irreversible** centrado en pantalla.

---

## ️ 3. Módulo: Gestión de Trabajos de Impresión (Print Jobs)

### Historia de Usuario 3: Eliminación Segura de Impresiones Bloqueadas (Locked Print)
> **Como** Operario de TI o Usuario final,  
> **Quiero** poder eliminar trabajos de impresión bloqueada retenidos en el disco duro de la impresora Ricoh directamente desde la interfaz web,  
> **Para** liberar espacio de almacenamiento y eliminar documentos confidenciales que no serán impresos.

#### Criterios de Aceptación (QA)
1.  La eliminación en WIM no debe dar falsos positivos. Se debe emular el flujo de JavaScript nativo de Ricoh (`common.js`) que envía un POST de confirmación final con `mode=3` conteniendo `baseID` y `kind` del trabajo.
2.  El frontend de Trabajos de Impresión debe ser 100% responsivo y usar todo el ancho horizontal de la pantalla, evitando barras de scroll horizontal incómodas en monitores Full HD.
3.  Se debe implementar una paginación interactiva arriba y abajo de la tabla que permita seleccionar cuántos registros visualizar (10, 25, 50, 100).

---

##  4. Enlaces de Diseño e Interfaz Visual (Mockups)

Los componentes y vistas responsivos deben replicar el estándar de diseño premium definido por el equipo de diseño en Figma (o directrices visuales del suite):
*   **Palette**: Fondo base `#FDFDFD`, barras y selectores premium con efecto vidrio (`backdrop-blur-md`), tipografías e iconos uniformes de Lucide.
*   **Aviso Irreversible**: Los modales de eliminación crítica deben presentarse con cabeceras de alerta roja, fondos en tono rojo suave (`bg-red-50`) e iconos de peligro (`AlertTriangle`).
