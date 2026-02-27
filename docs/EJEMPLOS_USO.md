# 📚 Ejemplos de Uso del Sistema

## Ejemplo 1: Usuario de Escáner Simple (1 Impresora)

### Escenario
Crear un usuario que solo necesita escanear documentos a una carpeta de red en una sola impresora.

### Pasos

1. **Información Básica**
   - Nombre: `María González`
   - Código: `1234`

2. **Autenticación de Carpeta**
   - Usuario: `reliteltda\scaner`
   - Contraseña: `tu_contraseña`

3. **Funciones Disponibles**
   - ☑️ Escáner
   - ☐ Copiadora
   - ☐ Impresora
   - ☐ Otras

4. **Carpeta SMB**
   - Ruta: `\\TIC0596\Escaner`

5. **Selección de Impresora**
   - Selecciona: `192.168.91.250` (1 impresora)

6. **Resultado**
   ```
   ✅ Usuario creado: María González (ID: 1)
   📡 Provisionando a 1 impresora(s)...
   ✅ Usuario provisionado a 192.168.91.250
   ✅ Configuración enviada exitosamente
   ```

---

## Ejemplo 2: Usuario Completo (Múltiples Impresoras)

### Escenario
Crear un usuario con acceso a todas las funciones en 3 impresoras del departamento de contabilidad.

### Pasos

1. **Información Básica**
   - Nombre: `Carlos Ramírez`
   - Código: `5678`

2. **Autenticación de Carpeta**
   - Usuario: `reliteltda\contabilidad`
   - Contraseña: `tu_contraseña`

3. **Funciones Disponibles**
   - ☑️ Escáner
   - ☑️ Copiadora (Blanco y Negro)
   - ☑️ Impresora (Blanco y Negro)
   - ☑️ Document Server
   - ☐ Fax
   - ☐ Navegador

4. **Carpeta SMB**
   - Ruta: `\\TIC0596\Contabilidad`

5. **Selección de Impresoras**
   - Selecciona: `192.168.91.250`
   - Selecciona: `192.168.91.251`
   - Selecciona: `192.168.91.252`
   - Total: 3 impresoras

6. **Resultado**
   ```
   ✅ Usuario creado: Carlos Ramírez (ID: 2)
   📡 Provisionando a 3 impresora(s)...
   🔐 Autenticando con impresora 192.168.91.250...
   ✅ Usuario provisionado a 192.168.91.250
   🔐 Autenticando con impresora 192.168.91.251...
   ✅ Usuario provisionado a 192.168.91.251
   🔐 Autenticando con impresora 192.168.91.252...
   ✅ Usuario provisionado a 192.168.91.252
   ✅ Configuración enviada exitosamente
   ```

---

## Ejemplo 3: Usuario con Color (Diseño Gráfico)

### Escenario
Crear un usuario del departamento de diseño que necesita copiar e imprimir a color en 2 impresoras específicas.

### Pasos

1. **Información Básica**
   - Nombre: `Ana Martínez`
   - Código: `9012`

2. **Autenticación de Carpeta**
   - Usuario: `reliteltda\diseno`
   - Contraseña: `tu_contraseña`

3. **Funciones Disponibles**
   - ☑️ Escáner
   - ☑️ Copiadora → **A todo color** ✓
   - ☑️ Impresora → **Color** ✓
   - ☐ Document Server
   - ☐ Fax
   - ☐ Navegador

4. **Carpeta SMB**
   - Ruta: `\\TIC0596\Diseno`

5. **Selección de Impresoras**
   - Selecciona: `192.168.91.253` (Impresora color 1)
   - Selecciona: `192.168.91.254` (Impresora color 2)
   - Total: 2 impresoras

6. **Resultado**
   ```
   ✅ Usuario creado: Ana Martínez (ID: 3)
   📡 Provisionando a 2 impresora(s)...
   ✅ Usuario provisionado a 192.168.91.253
   ✅ Usuario provisionado a 192.168.91.254
   ✅ Configuración enviada exitosamente
   ```

---

## Ejemplo 4: Aprovisionamiento Masivo (Todos los Equipos)

### Escenario
Crear un usuario administrador que necesita acceso a todas las impresoras de la empresa.

### Pasos

1. **Información Básica**
   - Nombre: `Admin TI`
   - Código: `0000`

2. **Autenticación de Carpeta**
   - Usuario: `reliteltda\admin`
   - Contraseña: `tu_contraseña`

3. **Funciones Disponibles**
   - ☑️ Todas las funciones habilitadas

4. **Carpeta SMB**
   - Ruta: `\\TIC0596\AdminTI`

5. **Selección de Impresoras**
   - Haz clic en **todas las tarjetas** de impresoras
   - Total: 10 impresoras (ejemplo)

6. **Resultado**
   ```
   ✅ Usuario creado: Admin TI (ID: 4)
   📡 Provisionando a 10 impresora(s)...
   ✅ Usuario provisionado a 192.168.91.250
   ✅ Usuario provisionado a 192.168.91.251
   ✅ Usuario provisionado a 192.168.91.252
   ... (8 más)
   ✅ Configuración enviada exitosamente
   ```

---

## Ejemplo 5: Manejo de Errores

### Escenario
Provisionar a 3 impresoras, pero una está apagada.

### Pasos

1. Completa el formulario normalmente
2. Selecciona 3 impresoras:
   - `192.168.91.250` (encendida)
   - `192.168.91.251` (apagada)
   - `192.168.91.252` (encendida)

3. **Resultado**
   ```
   ✅ Usuario creado: Juan Pérez (ID: 5)
   📡 Provisionando a 3 impresora(s)...
   ✅ Usuario provisionado a 192.168.91.250
   ❌ Error en 192.168.91.251: Connection timeout
   ✅ Usuario provisionado a 192.168.91.252
   ⚠️  Usuario provisionado a 2/3 impresoras
   ```

**Nota**: El sistema continúa con las demás impresoras aunque una falle.

---

## Ejemplo 6: Uso de Scripts de Prueba

### Prueba Simple (1 impresora)

```bash
cd backend
python test_final_v2.py
```

**Salida esperada:**
```
======================================================================
🧪 PRUEBA FINAL CON ÍNDICE ALEATORIO
======================================================================

📤 Provisionando usuario: TEST USER 6717
   Código: 6717
   Índice: 00999
   Usuario de red: reliteltda\scaner
   Impresora: 192.168.91.250

🔐 Autenticando con impresora 192.168.91.250...
✅ Ya autenticado o sin autenticación requerida
🔍 Paso 1: Obteniendo wimToken desde lista
✅ wimToken de lista obtenido: 123456789
🔍 Paso 2: Obteniendo formulario de añadir usuario
✅ wimToken FRESCO del formulario obtenido: 987654321
⚡ Paso 3: Enviando POST INMEDIATAMENTE
📤 Enviando datos de usuario
✅ User provisioned successfully to 192.168.91.250

======================================================================
✅ PROVISIONAMIENTO EXITOSO

💡 Verifica en la impresora:
   1. Ve a: http://192.168.91.250/web/entry/es/address/adrsList.cgi
   2. Busca el usuario con código: 6717
   3. Nombre: TEST USER 6717
======================================================================
```

### Prueba Múltiple (varias impresoras)

```bash
cd backend
python test_multi_printer_provisioning.py
```

**Salida esperada:**
```
======================================================================
🧪 PRUEBA DE APROVISIONAMIENTO A MÚLTIPLES IMPRESORAS
======================================================================

📤 Usuario a provisionar:
   Nombre: USUARIO MULTI 8234
   Código: 8234
   Usuario de red: reliteltda\scaner
   Funciones: Escáner

🖨️  Impresoras objetivo: 2
   1. 192.168.91.250
   2. 192.168.91.251

----------------------------------------------------------------------

📡 [1/2] Provisionando a 192.168.91.250...
   ✅ Éxito en 192.168.91.250

📡 [2/2] Provisionando a 192.168.91.251...
   ✅ Éxito en 192.168.91.251

======================================================================
📊 RESUMEN DE RESULTADOS
======================================================================

✅ Exitosos: 2/2
❌ Fallidos: 0/2

💡 Usuario 'USUARIO MULTI 8234' (código: 8234) 
   provisionado exitosamente en 2 impresora(s)

🔍 Verifica en las impresoras:
   • http://192.168.91.250/web/entry/es/address/adrsList.cgi
   • http://192.168.91.251/web/entry/es/address/adrsList.cgi

======================================================================
```

---

## Ejemplo 7: Verificación en la Impresora

### Pasos para verificar

1. Abre el navegador
2. Ve a: `http://[IP_IMPRESORA]/web/entry/es/address/adrsList.cgi`
3. Inicia sesión:
   - Usuario: `admin`
   - Contraseña: (dejar vacío)
4. Busca el usuario por código o nombre
5. Verifica los campos:
   - ✅ Nombre correcto
   - ✅ Código correcto
   - ✅ Usuario de red correcto
   - ✅ Carpeta SMB correcta
   - ✅ Funciones habilitadas correctas

---

## 🎯 Consejos Prácticos

### Para Usuarios Normales
- Habilita solo las funciones necesarias
- Usa Blanco y Negro por defecto (más económico)
- Provisiona solo a las impresoras cercanas al usuario

### Para Administradores
- Crea usuarios de prueba primero
- Verifica en una impresora antes de provisionar a todas
- Usa códigos de usuario únicos y fáciles de recordar

### Para Departamentos
- Usa nombres de usuario descriptivos: `Contabilidad - Juan`
- Agrupa impresoras por ubicación física
- Documenta qué usuarios tienen acceso a qué impresoras

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo cambiar la selección de impresoras después de hacer clic?**  
R: Sí, haz clic nuevamente en una tarjeta para deseleccionarla.

**P: ¿Qué pasa si no selecciono ninguna impresora?**  
R: El botón "Enviar Configuración" estará deshabilitado.

**P: ¿Puedo provisionar el mismo usuario a más impresoras después?**  
R: Sí, pero actualmente necesitas crear una nueva solicitud de aprovisionamiento.

**P: ¿Qué pasa si una impresora falla?**  
R: El sistema continúa con las demás y te muestra un resumen al final.

**P: ¿Cómo sé si el aprovisionamiento fue exitoso?**  
R: Revisa la consola en vivo y verifica en la interfaz web de la impresora.
