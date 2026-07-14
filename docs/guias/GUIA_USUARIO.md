# Manual de Usuario - Ricoh Equipment Manager Suite

Este manual detalla paso a paso como utilizar todas las funcionalidades del sistema Ricoh Equipment Manager para administrar impresoras, aprovisionar usuarios, consultar lecturas de contadores y realizar cierres mensuales de facturacion.

---

## 1. Acceso al Sistema y Seguridad de Sesion

### 1.1 Inicio de Sesion
1. Abra el navegador web e ingrese a la direccion del servidor local de produccion: `http://192.168.91.131` (o la IP asignada por su departamento de TI).
2. En la pantalla de inicio de sesion, ingrese sus credenciales de administrador:
   - **Usuario**: Su nombre de usuario (ej: `superadmin` o el asignado a su cuenta corporativa).
   - **Contrasena**: Ingrese su contrasena de seguridad (ej: `ricoh2026`).
3. Presione el boton **Iniciar Sesion**.

### 1.2 Bloqueo de Seguridad y Rate Limiting
*   **Politica de Bloqueo**: Si ingresa una contrasena incorrecta 5 veces consecutivas, su cuenta sera bloqueada de forma automatica durante 15 minutos por politicas de proteccion contra fuerza bruta.
*   **Rate Limiting**: Si realiza multiples solicitudes rapidas consecutivas, la pantalla mostrara un mensaje temporal de "Demasiados intentos. Por favor, intente mas tarde." provocado por el middleware anti-DDoS. El bloqueo expira tras esperar 60 segundos de inactividad.

### 1.3 Cierre de Sesion
1. Localice la tarjeta de usuario en la esquina inferior del menu lateral izquierdo.
2. Haga clic en su nombre de usuario.
3. Seleccione la opcion **Cerrar Sesion** para destruir el token JWT de forma segura e invalidar la sesion activa.

---

## 2. Administracion de Empresas y Usuarios Administradores (Solo Superadmin)

Estas opciones solo estan disponibles para los usuarios con el rol de Superadmin y permiten estructurar la jerarquia del sistema.

### 2.1 Gestion de Empresas (Multi-tenancy)
El sistema esta disenado bajo un modelo de Multi-tenancy. Cada empresa es un entorno aislado; los administradores estandar solo pueden visualizar las impresoras y usuarios de su respectiva empresa.

1. En el menu lateral izquierdo, dirijase a **Mis Empresas**.
2. **Crear una nueva Empresa**:
   - Presione el boton **Nueva Empresa**.
   - Complete el formulario: Razón Social (nombre legal), Nombre Comercial (formato unico en minusculas y separado por guiones como `mi-empresa-sas`), NIT (identificador tributario), Direccion, Telefono y los datos del contacto encargado.
   - Presione **Guardar**.
3. **Editar o Desactivar una Empresa**:
   - Utilice el buscador superior para localizar la empresa por NIT o razon social.
   - Presione **Editar** para actualizar la informacion de contacto.
   - Presione **Desactivar** para bloquear el acceso de esa empresa. El sistema impedira desactivar una empresa si aun tiene impresoras o usuarios activos vinculados.

### 2.2 Gestion de Usuarios Administradores del Sistema
1. En el menu lateral izquierdo, ingrese a **Administradores**.
2. **Crear un Administrador**:
   - Presione **Nuevo Administrador**.
   - Complete el formulario ingresando un nombre de usuario unico, contrasena segura, correo electronico y asigne un Rol:
     - **Superadmin**: Acceso a toda la plataforma y control de empresas.
     - **Admin**: Acceso exclusivo a los recursos e impresoras de la empresa asignada.
     - **Viewer**: Acceso de solo lectura para auditoria (sin permisos de escritura).
     - **Operator**: Permisos limitados a visualizacion de alertas y contadores.
   - Si selecciona un rol diferente a Superadmin, el sistema le obligara a elegir la **Empresa** a la que pertenecera el usuario.
   - Presione **Guardar**.

---

## 3. Busqueda y Descubrimiento de Equipos en Red

Este modulo le permite escanear e integrar nuevas impresoras Ricoh a la base de datos de control.

### 3.1 Escaneo y Registro de Equipos en Red
1. En el menu lateral izquierdo, dirijase a **Buscar Equipos**.
2. Presione el boton **Escanear Red** ubicado en la esquina superior derecha.
3. En el formulario emergente, especifique el rango de direcciones IP a escanear (ej: `192.168.91.100 - 192.168.91.254`).
4. Haga clic en **Comenzar Escaneo**. El sistema realizara una consulta asincrona en paralelo detectando los puertos Ricoh activos (80, 443, 161).
5. Al finalizar el escaneo, se listaran las impresoras detectadas junto con su hostname, direccion IP y numero de serie.
6. Seleccione las impresoras que desea registrar marcando la casilla de seleccion izquierda y presione **Registrar Dispositivos**.

---

## 4. Asignacion y Aprovisionamiento de Usuarios (Governance)

El modulo de Governance le permite crear perfiles de usuario e inyectar su configuracion directamente en la libreta de direcciones fisica de las impresoras Ricoh de forma remota.

### 4.1 Registrar un Nuevo Usuario en el Sistema
1. En el menu lateral izquierdo, ingrese a **Asignar Usuarios**.
2. En el panel izquierdo de la pantalla, complete los campos del formulario de creacion:
   - **Nombre**: Nombre completo del usuario (este sera el nombre visible en la pantalla fisica de la impresora).
   - **PIN / Codigo de Acceso**: Codigo numerico de 4 a 8 digitos con el cual el usuario iniciara sesion fisica en el teclado de la impresora.
   - **Email**: Correo corporativo del usuario (opcional).
   - **Departamento / Centro de Costos**: Identificador para la posterior facturacion.
3. En el selector de **Configuracion de Carpetas (SMB Scan-to-Folder)**, especifique la ruta de red donde se guardaran los documentos escaneados por el usuario (ej: `\\TIC0264\Escaner`) y sus credenciales de red (usuario y contrasena). El backend cifrara estas credenciales con algoritmo AES-256 antes de guardarlas en base de datos.
4. En el selector de **Permisos de Impresion**, defina si el usuario tiene permitido imprimir o copiar en color:
   - Marque **Copiadora Color** y **Permitir Impresion Color** si el usuario requiere acceso a color completo. Si se desmarcan, el usuario sera restringido estrictamente a Blanco y Negro en el firmware del equipo.
5. En el panel derecho de la pantalla, localice el listado de impresoras y marque la casilla de los equipos donde desea aprovisionar al usuario.
6. Presione **Enviar Configuracion**. El sistema iniciara un proceso en segundo plano conectandose a cada impresora seleccionada en paralelo. Una consola en vivo en la parte inferior de la pantalla reportara el estado del aprovisionamiento ("Autenticando en impresora...", "Usuario registrado en entry_index: 4", "Configuracion SMB completada").

### 4.2 Gestion de Usuarios y Desactivacion Logica
1. Dirijase a **Gestion de Usuarios** en el menu lateral.
2. En la parte superior de la pantalla, vera dos selectores principales: **Usuarios Activos** e **Usuarios Inactivos**.
3. Haga clic en la tarjeta de un usuario para desplegar la lista de equipos donde se encuentra enrolado.
4. **Desactivar un usuario en un equipo especifico**:
   - Presione el boton **Desactivar en este equipo** (representado con un icono de papelera al lado del nombre de la impresora).
   - Confirme la operacion en el cuadro emergente de confirmacion reactivo.
   - El sistema modificara el estado de la asignacion a `is_active = False` en base de datos. En la impresora fisica, deshabilitara todos los permisos del usuario de forma inmediata (bloqueando impresion y copias) pero **no eliminara al usuario de la libreta de direcciones**. Esto preserva el indice de entrada (`entry_index`) para evitar colisiones en futuros aprovisionamientos.
5. **Reactivar un usuario**:
   - Vaya a la pestana **Usuarios Inactivos**, seleccione al usuario y vuelva a asignar las impresoras deseadas presionando **Reactivar**.

---

## 5. Monitoreo de Suministros (Toner y Estado de Equipos)

El Dashboard principal del sistema le permite monitorear de forma visual e instantanea el estado y consumibles de toda su flota de impresoras.

### 5.1 Niveles de Toner y Alertas
1. En el menu lateral izquierdo, ingrese a **Resumen** (o Dashboard principal).
2. Cada impresora registrada se representara mediante una tarjeta interactiva que contiene:
   - **Indicadores de Toner**: 4 barras dinamicas que representan el porcentaje restante de Cyan, Magenta, Amarillo (Yellow) y Negro (Black) en tiempo real. En impresoras monocromaticas (Blanco y Negro), la tarjeta ocultara automaticamente los tóners de color y solo mostrara la barra de toner Negro.
   - **Estado de Conexion**: Un indicador verde si el dispositivo responde activamente en la red (Online) o rojo si se encuentra apagado o inaccesible (Offline).
   - **Unidad de Sostenibilidad Ecologica**: Muestra las estadisticas y metricas del impacto ecologico del equipo basado en las paginas impresas a doble cara.

---

## 6. Lectura de Contadores y Cierres Mensuales

Este modulo permite recolectar los contadores fisicos de las impresoras para la facturacion mensual y generar comparativas de consumo.

### 6.1 Visualizar Contadores en Vivo
1. Ingrese a **Lectura de Contadores** en el menu lateral.
2. Seleccione un **Dispositivo Escaneado** de la lista desplegable en la barra de filtros premium (ej: `RNP002673721B98 (192.168.91.253)`).
3. Seleccione el **Periodo Anual** a consultar (ej: `2026`).
4. Si la impresora seleccionada es valida, se desplegara el listado de cierres historicos organizados de forma cronologica.
5. Cada tarjeta de cierre detalla:
   - Rango de fechas del periodo evaluado.
   - **Contador Global**: Paginas totales registradas en el dispositivo.
   - **Desglose de Totales**: Copiadora, Impresora, Escaneo y Fax.
   - **Gasto en Periodo**: Paginas consumidas unicamente en el rango de fechas evaluado.
   - Nombre de la persona o sistema que ejecuto el cierre.

### 6.2 Ejecutar un Cierre Mensual Individual
1. En la barra superior de filtros de la pantalla **Lectura de Contadores**, presione **Cierre Individual**.
2. En el formulario flotante:
   - Especifique la fecha de inicio y la fecha de fin del periodo contable.
   - El sistema realizara una consulta remota en la impresora para capturar el snapshot de contadores de cada usuario activo y del dispositivo general.
3. Presione **Guardar Cierre**. El cierre quedara registrado y se generara la comparativa de consumos.

### 6.3 Ejecutar un Cierre Masivo de la Flota
Si necesita consolidar las lecturas de multiples impresoras al finalizar el mes sin hacerlo una por una:
1. En la esquina superior derecha del modulo de contadores, haga clic en el boton **Cierre Masivo**.
2. En el modal emergente:
   - Escriba un nombre para identificar el periodo (ej: `Cierre Consolidado Julio 2026`).
   - Defina el rango de fechas del periodo.
   - Seleccione mediante las casillas de verificacion todas las impresoras que desea incluir en el proceso.
3. Haga clic en **Procesar Cierre Masivo**. El backend utilizara workers concurrentes para interrogar a todos los dispositivos en paralelo y registrar sus respectivos snapshots de contadores individuales.

### 6.4 Generar e Importar Comparativas
1. Si dispone de dos o mas cierres mensuales registrados, presione el boton **Comparativa** en la barra superior.
2. Seleccione el primer mes de referencia y el segundo mes a contrastar.
3. El sistema generara un grafico comparativo dinamico detallando el incremento o decremento de paginas impresas por cada usuario.
4. Para guardar el reporte de comparativa, presione **Guardar Comparacion** en la esquina superior derecha, asigne un titulo y una descripcion. Este reporte podra consultarse en cualquier momento desde la seccion **Comparaciones Guardadas** del dashboard del modulo.

### 6.5 Exportar Reportes a Formato Oficial Ricoh (Excel)
1. Ingrese a los detalles de cualquier cierre guardado haciendo clic en **Ver Detalles** en la tarjeta de cierre.
2. Presione el boton **Exportar Excel**.
3. El sistema generara de forma automatica un libro de Excel estructurado en 3 hojas bajo el formato Ricoh oficial:
   - **Hoja 1 (Resumen)**: Datos generales de la impresora, serial, IP y totales de consumo.
   - **Hoja 2 (Consumo por Centros de Costo)**: Agrupacion y costos calculados por departamento.
   - **Hoja 3 (Detalle de Usuarios)**: Consumo individualizado por cada codigo PIN registrado.
4. El archivo se descargara en su navegador con la nomenclatura oficial automatizada: `SERIAL_DD.MM.YYYY.xlsx` (donde SERIAL es el serial de la impresora consultada y la fecha corresponde al dia del cierre).

### 6.6 Eliminar un Cierre Mensual
1. Localice el cierre mensual en el **Historial de Cierres**.
2. Presione el boton de **Papelera** (🗑️) ubicado en la esquina superior derecha de la tarjeta de cierre.
3. En pantalla aparecera el modal de confirmacion de **Accion Irreversible** perfectamente centrado.
4. Si esta seguro de descartar las lecturas, haga clic en el boton rojo **Eliminar Cierre**. Esto eliminara de forma permanente el registro del cierre y todos los historiales de consumos asociados de los usuarios en la base de datos en cascada.

---

## 7. Reportes y Analytics (Consumos y Tendencias)

El modulo de Analisis proporciona herramientas visuales avanzadas para identificar los habitos de impresion y costes de la organizacion.

### 7.1 Panel de Analytics
1. En el menu lateral izquierdo, ingrese a **Reportes & Analytics**.
2. **Filtros Dinamicos**: En la parte superior, seleccione el periodo a evaluar mediante los dropdowns. Estos periodos se cargan de forma dinamica consultando los cierres reales registrados en la base de datos (`uniquePeriods`).
3. El modulo cargara 3 sub-paneles:
   - **Consumo por Usuario**: Grafico de barras detallando las paginas impresas por cada codigo PIN.
   - **Consumo por Centro de Costos**: Distribucion porcentual del consumo (Administracion, Logistica, TI, etc.).
   - **Tendencia Temporal**: Grafico de lineas mostrando el comportamiento del volumen de impresion a lo largo del ano.

---

## 8. Administracion de Trabajos de Impresion (Print Jobs)

El modulo de Trabajos de Impresion permite gestionar en vivo las colas de impresion de una o multiples impresoras en paralelo para tareas de mantenimiento y auditoria de documentos confidenciales.

### 8.1 Consultar Cola de Impresion Multi-Impresora
1. En el menu lateral izquierdo, ingrese a **Trabajos de Impresion**.
2. En la barra superior, seleccione una o mas impresoras marcando las casillas del selector desplegable.
3. El sistema realizara consultas concurrentes en segundo plano usando multiples hilos y cargara la tabla unificada de trabajos.
4. La tabla detalla:
   - **Dispositivo**: Impresora donde reside el trabajo.
   - **Usuario**: Creador del documento.
   - **Nombre del Documento**: Titulo del archivo en cola.
   - **Tipo**: Identificador del trabajo (Impresion Normal, Impresion Bloqueada / Locked Print, etc.).
   - **Estado**: Esperando / Retenido / En proceso.
   - **Fecha de Recepcion**: Hora de llegada al disco duro.

### 8.2 Eliminar Trabajos de Impresion Retenidos o Bloqueados
1. En la tabla de trabajos, localice el archivo que desea remover.
2. Haga clic en el boton de **Eliminacion** (🗑️) de la fila.
3. El backend ejecutara una rutina segura en dos pasos: realizara la llamada de seleccion de trabajo a WIM, analizara el formulario de respuesta e inyectara la confirmacion final de borrado (`mode=3`).
4. Al completarse la accion, la tabla se actualizara en vivo y el documento desaparecera del disco duro de la impresora.
