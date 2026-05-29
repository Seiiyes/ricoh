# Problema Detectado: Match entre CSV Contador y Comparativo

## 🔍 Problema Encontrado

Al comparar exhaustivamente los CSV, se detectó que **G986XA16285** y **E174MA11130** tienen formatos INCOMPATIBLES entre el CSV contador y el CSV comparativo:

### CSV Contador (G986 y E174)
```
Usuario,Nombre,Total impresiones,...
[1717],[YESICA GARCIA],0,...
[YEISON DURANGO],[YEISON DURANGO],21332,...
[MANTENIMIENTO],[MANTENIMIENTO],6066,...
```

**Formato**: `[NOMBRE]` o `[CÓDIGO]` - INCONSISTENTE

### CSV Comparativo (G986 y E174)
```
Usuario,Nombre,B/N,COLOR,TOTAL IMPRESIONES,...
[1717],[YESICA GARCIA],0.0,0.0,0,...
[0742],[YEISON DURANGO],3209.0,0.0,3209,...
[2902],[MANTENIMIENTO],241.0,0.0,241,...
```

**Formato**: `[CÓDIGO_NUMÉRICO]` - CONSISTENTE

## 📊 Ejemplos de Inconsistencia

| Nombre | CSV Contador | CSV Comparativo | Match |
|--------|--------------|-----------------|-------|
| YEISON DURANGO | `[YEISON DURANGO]` | `[0742]` | ❌ NO |
| MANTENIMIENTO | `[MANTENIMIENTO]` | `[2902]` | ❌ NO |
| YESICA GARCIA | `[1717]` | `[1717]` | ✅ SÍ |

## 🔢 Estadísticas

### W533L900719
- ✅ Match perfecto: 183/183 usuarios
- ✅ Coherencia: 99.9%

### G986XA16285
- ❌ Match: 0/87 usuarios
- ⚠️  87 huérfanos en contador
- ⚠️  87 huérfanos en comparativo
- ✅ Coherencia de sumas: 100.0%

### E174MA11130
- ❌ Match: 0/257 usuarios
- ⚠️  257 huérfanos en contador
- ⚠️  262 huérfanos en comparativo
- ✅ Coherencia de sumas: 101.2%

## 💡 Soluciones Posibles

### Opción 1: Match por Nombre (RECOMENDADA)
Hacer el match entre CSV usando el NOMBRE del usuario en lugar del código.

**Ventajas**:
- Funciona con los datos actuales
- No requiere modificar CSV
- Robusto ante variaciones de código

**Desventajas**:
- Sensible a diferencias en nombres (acentos, espacios)
- Requiere normalización de nombres

### Opción 2: Corregir CSV Contador
Modificar el CSV contador para que use códigos numéricos consistentes.

**Ventajas**:
- Match perfecto por código
- Más confiable a largo plazo

**Desventajas**:
- Requiere modificar archivos fuente
- Trabajo manual

### Opción 3: Usar Ambos CSV Comparativos
Usar solo los CSV comparativos que tienen toda la información.

**Ventajas**:
- Datos consistentes
- No requiere match

**Desventajas**:
- Pierde información detallada del CSV contador
- Menos campos disponibles

## 🎯 Recomendación

**Usar Opción 1: Match por Nombre**

Implementar un sistema de match que:
1. Normalice nombres (quitar acentos, mayúsculas, espacios extra)
2. Haga match por nombre normalizado
3. Registre matches exitosos y fallidos
4. Permita revisión manual de casos ambiguos

## 📝 Implementación Propuesta

```python
def normalizar_nombre(nombre: str) -> str:
    """Normaliza un nombre para hacer match"""
    import unicodedata
    # Remover acentos
    nombre = unicodedata.normalize('NFKD', nombre)
    nombre = nombre.encode('ASCII', 'ignore').decode('ASCII')
    # Mayúsculas, sin espacios extra
    nombre = ' '.join(nombre.upper().split())
    return nombre

def hacer_match_por_nombre(usuarios_contador, usuarios_comparativo):
    """Hace match entre usuarios por nombre"""
    # Crear índice por nombre normalizado
    indice_comparativo = {}
    for codigo, datos in usuarios_comparativo.items():
        nombre_norm = normalizar_nombre(datos['nombre'])
        indice_comparativo[nombre_norm] = {
            'codigo': codigo,
            'datos': datos
        }
    
    # Hacer match
    matches = []
    sin_match = []
    
    for usuario in usuarios_contador:
        nombre_norm = normalizar_nombre(usuario['nombre'])
        
        if nombre_norm in indice_comparativo:
            match = indice_comparativo[nombre_norm]
            usuario['consumo_total'] = match['datos']['consumo']
            usuario['codigo_comparativo'] = match['codigo']
            matches.append(usuario)
        else:
            usuario['consumo_total'] = 0
            sin_match.append(usuario)
    
    return matches, sin_match
```

## ⚠️  Advertencias

1. **Nombres duplicados**: Si hay usuarios con el mismo nombre, el match puede fallar
2. **Variaciones de nombre**: Diferencias mínimas en nombres pueden causar no-match
3. **Códigos inconsistentes**: Los códigos en el CSV contador no son confiables para G986/E174

## 🔄 Próximos Pasos

1. Implementar función de normalización de nombres
2. Actualizar función de lectura de CSV detallado
3. Implementar match por nombre
4. Agregar logging de matches exitosos/fallidos
5. Probar con datos reales
6. Validar resultados

---

**Fecha**: 2026-03-16
**Estado**: PROBLEMA IDENTIFICADO - Requiere implementación de match por nombre
