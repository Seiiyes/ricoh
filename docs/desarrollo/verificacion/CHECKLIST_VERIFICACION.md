# ✅ Checklist de Verificación del Sistema

## 🎯 Verificación Completa de Funcionalidad

Usa este checklist para verificar que el sistema funciona correctamente.

---

## 1. Verificación de Infraestructura

### Base de Datos
- [ ] PostgreSQL está ejecutándose
- [ ] Base de datos `ricoh_provisioning` existe
- [ ] Tablas creadas correctamente:
  - [ ] `users`
  - [ ] `printers`
  - [ ] `user_printer_assignments`
- [ ] Migraciones aplicadas

**Comando de verificación:**
```bash
docker ps | grep postgres
```

### Backend
- [ ] FastAPI está ejecutándose en `http://localhost:8000`
- [ ] API responde correctamente
- [ ] Logs no muestran errores

**Comando de verificación:**
```bash
curl http://localhost:8000/docs
```

### Frontend
- [ ] React está ejecutándose en `http://localhost:5173`
- [ ] Interfaz carga correctamente
- [ ] No hay errores en la consola del navegador

**Comando de verificación:**
```bash
# Abre el navegador en http://localhost:5173
```

---

## 2. Verificación de Descubrimiento de Impresoras

- [ ] Botón "Descubrir Impresoras" funciona
- [ ] Modal de descubrimiento se abre
- [ ] Puedes ingresar rango de red (ej: `192.168.91.0/24`)
- [ ] El escaneo encuentra impresoras
- [ ] Las impresoras aparecen en la cuadrícula
- [ ] Cada tarjeta muestra:
  - [ ] IP
  - [ ] Hostname
  - [ ] Modelo
  - [ ] Estado

---

## 3. Verificación de Formulario de Usuario

### Campos Básicos
- [ ] Campo "Nombre Completo" acepta texto
- [ ] Campo "Código de Usuario" acepta solo números
- [ ] Campo "Código de Usuario" limita a 8 caracteres

### Autenticación de Carpeta
- [ ] Campo "Nombre de usuario de inicio de sesión" funciona
- [ ] Campo "Contraseña de inicio de sesión" es tipo password
- [ ] Contraseña se oculta con asteriscos

### Funciones Disponibles
- [ ] Checkbox "Copiadora" funciona
  - [ ] Al marcar, aparecen opciones de color
  - [ ] Radio buttons "A todo color" / "Blanco y Negro" funcionan
- [ ] Checkbox "Impresora" funciona
  - [ ] Al marcar, aparecen opciones de color
  - [ ] Radio buttons "Color" / "Blanco y Negro" funcionan
- [ ] Checkbox "Document Server" funciona
- [ ] Checkbox "Fax" funciona
- [ ] Checkbox "Escáner" funciona (marcado por defecto)
- [ ] Checkbox "Navegador" funciona

### Carpeta SMB
- [ ] Campo "Ruta" acepta rutas UNC
- [ ] Placeholder muestra formato correcto

---

## 4. Verificación de Selección de Impresoras

- [ ] Puedes hacer clic en una tarjeta de impresora
- [ ] La tarjeta seleccionada muestra borde rojo
- [ ] Puedes hacer clic en múltiples tarjetas
- [ ] Puedes deseleccionar haciendo clic nuevamente
- [ ] Contador muestra "Seleccionadas: X impresora(s)"
- [ ] El número actualiza correctamente

---

## 5. Verificación de Aprovisionamiento

### Caso 1: Una Impresora
- [ ] Completa el formulario
- [ ] Selecciona 1 impresora
- [ ] Haz clic en "Enviar Configuración"
- [ ] Consola muestra:
  - [ ] "Usuario creado: [nombre] (ID: [id])"
  - [ ] "Provisionando a 1 impresora(s)..."
  - [ ] "Usuario provisionado a [IP]"
  - [ ] "Configuración enviada exitosamente"
- [ ] Formulario se limpia
- [ ] Selección se resetea

### Caso 2: Múltiples Impresoras
- [ ] Completa el formulario
- [ ] Selecciona 2 o más impresoras
- [ ] Haz clic en "Enviar Configuración"
- [ ] Consola muestra progreso para cada impresora
- [ ] Mensaje final indica cuántas fueron exitosas

### Caso 3: Todas las Impresoras
- [ ] Completa el formulario
- [ ] Selecciona todas las impresoras disponibles
- [ ] Haz clic en "Enviar Configuración"
- [ ] Sistema provisiona a todas correctamente

---

## 6. Verificación en la Impresora

Para cada impresora provisionada:

- [ ] Accede a `http://[IP]/web/entry/es/address/adrsList.cgi`
- [ ] Inicia sesión (admin / sin contraseña)
- [ ] Busca el usuario por código
- [ ] Verifica que el usuario aparece en la lista
- [ ] Haz clic en el usuario para ver detalles
- [ ] Verifica campos:
  - [ ] Nombre correcto
  - [ ] Código correcto
  - [ ] Usuario de red correcto
  - [ ] Carpeta SMB correcta
  - [ ] Funciones habilitadas correctas

---

## 7. Verificación de Base de Datos

### Tabla `users`
```sql
SELECT * FROM users ORDER BY created_at DESC LIMIT 5;
```

Verifica:
- [ ] Usuario creado existe
- [ ] Nombre correcto
- [ ] Código correcto
- [ ] Contraseña encriptada (no en texto plano)
- [ ] Funciones guardadas correctamente

### Tabla `user_printer_assignments`
```sql
SELECT * FROM user_printer_assignments 
WHERE user_id = [ID_USUARIO];
```

Verifica:
- [ ] Asignaciones creadas para cada impresora
- [ ] `user_id` correcto
- [ ] `printer_id` correcto
- [ ] Fecha de creación correcta

---

## 8. Verificación de Seguridad

- [ ] Contraseñas se almacenan encriptadas
- [ ] Contraseñas no aparecen en logs
- [ ] Contraseñas no aparecen en respuestas de API
- [ ] Solo se desencriptan durante aprovisionamiento

**Verificación:**
```sql
SELECT network_password_encrypted FROM users LIMIT 1;
```
Debe mostrar texto encriptado, no la contraseña real.

---

## 9. Verificación de Manejo de Errores

### Impresora Apagada
- [ ] Selecciona una impresora apagada
- [ ] Intenta provisionar
- [ ] Sistema muestra error en consola
- [ ] Sistema continúa con otras impresoras
- [ ] Resumen indica cuántas fallaron

### Campos Vacíos
- [ ] Intenta enviar sin nombre
- [ ] Botón está deshabilitado
- [ ] Intenta enviar sin código
- [ ] Botón está deshabilitado
- [ ] Intenta enviar sin contraseña
- [ ] Botón está deshabilitado

### Sin Impresoras Seleccionadas
- [ ] Completa el formulario
- [ ] No selecciones ninguna impresora
- [ ] Botón "Enviar Configuración" está deshabilitado

---

## 10. Verificación de Scripts de Prueba

### Test Simple
```bash
cd backend
python test_final_v2.py
```

- [ ] Script ejecuta sin errores
- [ ] Muestra "PROVISIONAMIENTO EXITOSO"
- [ ] Usuario aparece en la impresora

### Test Múltiple
```bash
cd backend
python test_multi_printer_provisioning.py
```

- [ ] Script ejecuta sin errores
- [ ] Provisiona a todas las impresoras configuradas
- [ ] Muestra resumen de resultados

---

## 11. Verificación de Consola en Vivo

- [ ] Consola muestra eventos en tiempo real
- [ ] Mensajes de éxito en verde
- [ ] Mensajes de error en rojo
- [ ] Mensajes de info en blanco
- [ ] Auto-scroll funciona
- [ ] Timestamps correctos

---

## 12. Verificación de Funciones Adicionales

### Editar Impresora
- [ ] Haz clic en ícono de lápiz
- [ ] Modal de edición se abre
- [ ] Puedes modificar campos
- [ ] Cambios se guardan correctamente

### Refrescar SNMP
- [ ] Haz clic en ícono de actualización
- [ ] Sistema consulta SNMP
- [ ] Datos se actualizan
- [ ] Consola muestra confirmación

---

## 📊 Resumen de Verificación

### Componentes Críticos
- [ ] Base de datos funcional
- [ ] Backend funcional
- [ ] Frontend funcional
- [ ] Descubrimiento de impresoras funcional
- [ ] Formulario de usuario funcional
- [ ] Selección múltiple funcional
- [ ] Aprovisionamiento funcional
- [ ] Verificación en impresora exitosa

### Flujo Completo
- [ ] Descubrir impresoras → ✅
- [ ] Crear usuario → ✅
- [ ] Seleccionar impresoras → ✅
- [ ] Provisionar → ✅
- [ ] Verificar en impresora → ✅

---

## 🎯 Criterios de Éxito

El sistema está **completamente funcional** si:

1. ✅ Todos los componentes de infraestructura están ejecutándose
2. ✅ Puedes descubrir impresoras en la red
3. ✅ Puedes crear usuarios con todos los campos
4. ✅ Puedes seleccionar una o múltiples impresoras
5. ✅ El aprovisionamiento es exitoso
6. ✅ Los usuarios aparecen en las impresoras
7. ✅ La base de datos refleja las asignaciones
8. ✅ Los errores se manejan correctamente

---

## 🐛 Problemas Comunes y Soluciones

### Problema: Base de datos no conecta
**Solución:**
```bash
docker-compose down
docker-compose up -d
```

### Problema: Backend no inicia
**Solución:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Problema: Frontend no carga
**Solución:**
```bash
npm install
npm run dev
```

### Problema: Usuario no aparece en impresora
**Solución:**
1. Verifica que la impresora esté accesible
2. Revisa la consola para ver errores
3. Ejecuta `python backend/test_final_v2.py` para diagnóstico

---

## 📝 Registro de Verificación

**Fecha:** _______________  
**Verificado por:** _______________  
**Resultado:** ☐ Exitoso  ☐ Con problemas  
**Notas:** _______________________________________________
