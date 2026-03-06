#!/usr/bin/env python3
"""
Close Service - Servicio unificado para cierres de contadores
Soporta cierres diarios, semanales, mensuales y personalizados
"""
import sys
import os
from typing import Optional, Dict
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import hashlib
import calendar

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import Printer, ContadorImpresora, ContadorUsuario, CierreMensual, CierreMensualUsuario


class CloseService:
    """Servicio unificado para cierres de contadores"""
    
    @staticmethod
    def create_close(
        db: Session,
        printer_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        tipo_periodo: str = 'personalizado',
        cerrado_por: Optional[str] = None,
        notas: Optional[str] = None,
        validar_secuencia: bool = True
    ) -> CierreMensual:
        """
        Crea un cierre de contadores para cualquier período
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            tipo_periodo: Tipo de período ('diario', 'semanal', 'mensual', 'personalizado')
            cerrado_por: Usuario que realiza el cierre
            notas: Notas adicionales
            validar_secuencia: Si True, valida que no haya gaps en cierres mensuales
            
        Returns:
            CierreMensual creado con snapshot de usuarios
            
        Raises:
            ValueError: Si hay errores de validación
            
        Examples:
            # Cierre diario
            create_close(db, 1, date(2026, 3, 3), date(2026, 3, 3), 'diario')
            
            # Cierre semanal
            create_close(db, 1, date(2026, 3, 1), date(2026, 3, 7), 'semanal')
            
            # Cierre mensual
            create_close(db, 1, date(2026, 3, 1), date(2026, 3, 31), 'mensual')
        """
        
        # ====================================================================
        # VALIDACIONES PREVIAS
        # ====================================================================
        
        # 1. Validar tipo de período
        tipos_validos = ['diario', 'semanal', 'mensual', 'personalizado']
        if tipo_periodo not in tipos_validos:
            raise ValueError(f"Tipo de período inválido. Debe ser uno de: {', '.join(tipos_validos)}")
        
        # 2. Validar fechas
        if fecha_fin < fecha_inicio:
            raise ValueError("La fecha de fin debe ser mayor o igual a la fecha de inicio")
        
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        if dias_periodo > 365:
            raise ValueError("El período no puede ser mayor a 1 año")
        
        # 3. Verificar que la impresora existe
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            raise ValueError(f"Impresora {printer_id} no encontrada")
        
        # 4. Verificar que no exista cierre duplicado del mismo tipo y período
        # Permitir solapamientos de diferentes tipos (ej: mensual + diarios)
        duplicado = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id,
            CierreMensual.tipo_periodo == tipo_periodo,
            CierreMensual.fecha_inicio == fecha_inicio,
            CierreMensual.fecha_fin == fecha_fin
        ).first()
        
        if duplicado:
            raise ValueError(
                f"Ya existe un cierre {tipo_periodo} para el período {fecha_inicio} a {fecha_fin}. "
                f"Cerrado por: {duplicado.cerrado_por or 'N/A'} "
                f"Fecha: {duplicado.fecha_cierre.strftime('%Y-%m-%d %H:%M')}"
            )
        
        # 5. Validar que el período no sea futuro
        fecha_actual = date.today()
        if fecha_inicio > fecha_actual:
            raise ValueError("No se puede cerrar un período futuro")
        
        # 6. Para cierres mensuales, validar que el mes esté completo
        if tipo_periodo == 'mensual':
            # Verificar que fecha_inicio sea el primer día del mes
            if fecha_inicio.day != 1:
                raise ValueError("Un cierre mensual debe iniciar el día 1 del mes")
            
            # Verificar que fecha_fin sea el último día del mes
            ultimo_dia = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
            if fecha_fin.day != ultimo_dia:
                raise ValueError(f"Un cierre mensual debe terminar el día {ultimo_dia} del mes")
            
            # No se puede cerrar el mes actual
            if fecha_inicio.year == fecha_actual.year and fecha_inicio.month == fecha_actual.month:
                raise ValueError(
                    f"No se puede cerrar el mes actual ({fecha_inicio.year}-{fecha_inicio.month:02d}). "
                    f"Debe esperar a que termine el mes."
                )
        
        # 7. Obtener contador más cercano a la fecha de fin del período
        # Para cierres diarios, usar el último contador de ese día
        # Para cierres mensuales, usar el último contador del mes
        fecha_fin_datetime = datetime.combine(fecha_fin, datetime.max.time())
        
        ultimo_contador = db.query(ContadorImpresora).filter(
            ContadorImpresora.printer_id == printer_id,
            ContadorImpresora.fecha_lectura <= fecha_fin_datetime
        ).order_by(ContadorImpresora.fecha_lectura.desc()).first()
        
        if not ultimo_contador:
            raise ValueError(f"No hay contadores registrados hasta {fecha_fin} para impresora {printer_id}")
        
        # 8. Validar que el contador sea reciente (máximo 7 días)
        fecha_lectura_naive = ultimo_contador.fecha_lectura.replace(tzinfo=None) if ultimo_contador.fecha_lectura.tzinfo else ultimo_contador.fecha_lectura
        dias_antiguedad = (datetime.now() - fecha_lectura_naive).days
        if dias_antiguedad > 7:
            raise ValueError(
                f"El último contador tiene {dias_antiguedad} días de antigüedad. "
                f"Ejecute una lectura manual antes de cerrar."
            )
        
        # 9. Obtener cierre anterior (el más reciente antes de este período)
        cierre_anterior = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id,
            CierreMensual.fecha_fin < fecha_inicio
        ).order_by(CierreMensual.fecha_fin.desc()).first()
        
        # 10. Para cierres mensuales, validar secuencia
        if tipo_periodo == 'mensual' and validar_secuencia and cierre_anterior:
            # Verificar que no haya gaps en cierres mensuales
            if cierre_anterior.tipo_periodo == 'mensual':
                # Calcular el mes siguiente al cierre anterior
                if cierre_anterior.mes == 12:
                    mes_esperado = 1
                    anio_esperado = cierre_anterior.anio + 1
                else:
                    mes_esperado = cierre_anterior.mes + 1
                    anio_esperado = cierre_anterior.anio
                
                # Verificar que este cierre sea el mes siguiente
                if fecha_inicio.year != anio_esperado or fecha_inicio.month != mes_esperado:
                    raise ValueError(
                        f"Debe cerrar {anio_esperado}-{mes_esperado:02d} antes de cerrar "
                        f"{fecha_inicio.year}-{fecha_inicio.month:02d}"
                    )
        
        # 11. Detectar reset de contador
        if cierre_anterior and ultimo_contador.total < cierre_anterior.total_paginas:
            raise ValueError(
                f"⚠️  RESET DE CONTADOR DETECTADO\n"
                f"Contador anterior: {cierre_anterior.total_paginas:,}\n"
                f"Contador actual: {ultimo_contador.total:,}\n"
                f"Diferencia: {ultimo_contador.total - cierre_anterior.total_paginas:,}\n\n"
                f"ACCIÓN REQUERIDA:\n"
                f"1. Verificar si hubo mantenimiento en la impresora\n"
                f"2. Contactar al técnico para confirmar reset\n"
                f"3. Ajustar manualmente el cierre\n"
                f"4. Documentar el incidente en 'notas'"
            )
        
        # ====================================================================
        # CALCULAR TOTALES ACTUALES
        # ====================================================================
        
        total_paginas = ultimo_contador.total
        total_copiadora = max(
            ultimo_contador.copiadora_bn,
            ultimo_contador.copiadora_color,
            ultimo_contador.copiadora_color_personalizado,
            ultimo_contador.copiadora_dos_colores
        )
        total_impresora = max(
            ultimo_contador.impresora_bn,
            ultimo_contador.impresora_color,
            ultimo_contador.impresora_color_personalizado,
            ultimo_contador.impresora_dos_colores
        )
        total_escaner = max(
            ultimo_contador.envio_escaner_bn,
            ultimo_contador.envio_escaner_color
        )
        total_fax = ultimo_contador.fax_bn
        
        # ====================================================================
        # CALCULAR DIFERENCIAS CON CIERRE ANTERIOR
        # ====================================================================
        
        if cierre_anterior:
            diferencia_total = total_paginas - cierre_anterior.total_paginas
            diferencia_copiadora = total_copiadora - cierre_anterior.total_copiadora
            diferencia_impresora = total_impresora - cierre_anterior.total_impresora
            diferencia_escaner = total_escaner - cierre_anterior.total_escaner
            diferencia_fax = total_fax - cierre_anterior.total_fax
        else:
            # Primer cierre, no hay diferencias
            diferencia_total = 0
            diferencia_copiadora = 0
            diferencia_impresora = 0
            diferencia_escaner = 0
            diferencia_fax = 0
        
        # ====================================================================
        # CREAR CIERRE
        # ====================================================================
        
        try:
            db.begin_nested()
            
            cierre = CierreMensual(
                printer_id=printer_id,
                tipo_periodo=tipo_periodo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                anio=fecha_inicio.year,
                mes=fecha_inicio.month,
                
                # Totales
                total_paginas=total_paginas,
                total_copiadora=total_copiadora,
                total_impresora=total_impresora,
                total_escaner=total_escaner,
                total_fax=total_fax,
                
                # Diferencias
                diferencia_total=diferencia_total,
                diferencia_copiadora=diferencia_copiadora,
                diferencia_impresora=diferencia_impresora,
                diferencia_escaner=diferencia_escaner,
                diferencia_fax=diferencia_fax,
                
                fecha_cierre=datetime.now(),
                cerrado_por=cerrado_por,
                notas=notas
            )
            
            db.add(cierre)
            db.flush()
            
            # ====================================================================
            # CREAR SNAPSHOT DE USUARIOS
            # ====================================================================
            
            usuarios_snapshot = []
            
            usuarios_codigos = db.query(ContadorUsuario.codigo_usuario).filter(
                ContadorUsuario.printer_id == printer_id
            ).distinct().all()
            
            for (codigo,) in usuarios_codigos:
                consumo = CloseService._calcular_consumo_usuario(
                    db, printer_id, codigo, fecha_inicio, fecha_fin, cierre_anterior
                )
                
                if consumo:
                    usuario_cierre = CierreMensualUsuario(
                        cierre_mensual_id=cierre.id,
                        codigo_usuario=consumo['codigo_usuario'],
                        nombre_usuario=consumo['nombre_usuario'],
                        
                        total_paginas=consumo['contador_actual'],
                        total_bn=consumo['total_bn'],
                        total_color=consumo['total_color'],
                        
                        copiadora_bn=consumo['copiadora_bn'],
                        copiadora_color=consumo['copiadora_color'],
                        impresora_bn=consumo['impresora_bn'],
                        impresora_color=consumo['impresora_color'],
                        escaner_bn=consumo['escaner_bn'],
                        escaner_color=consumo['escaner_color'],
                        fax_bn=consumo['fax_bn'],
                        
                        consumo_total=consumo['consumo_total'],
                        consumo_copiadora=consumo['consumo_copiadora'],
                        consumo_impresora=consumo['consumo_impresora'],
                        consumo_escaner=consumo['consumo_escaner'],
                        consumo_fax=consumo['consumo_fax']
                    )
                    usuarios_snapshot.append(usuario_cierre)
            
            if not usuarios_snapshot:
                raise ValueError("No hay usuarios para guardar en snapshot")
            
            db.bulk_save_objects(usuarios_snapshot)
            db.flush()
            
            # ====================================================================
            # VALIDACIONES DE INTEGRIDAD
            # ====================================================================
            
            count = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == cierre.id
            ).count()
            
            if count != len(usuarios_snapshot):
                raise ValueError(
                    f"Error de integridad: se esperaban {len(usuarios_snapshot)} usuarios, "
                    f"se guardaron {count}"
                )
            
            if diferencia_total > 0:
                suma_consumos = db.query(
                    func.sum(CierreMensualUsuario.consumo_total)
                ).filter(
                    CierreMensualUsuario.cierre_mensual_id == cierre.id
                ).scalar() or 0
                
                diferencia_porcentual = abs(suma_consumos - diferencia_total) / diferencia_total if diferencia_total > 0 else 0
                
                if diferencia_porcentual > 0.10:
                    nota_diferencia = (
                        f"\n\n⚠️  ADVERTENCIA DE CONSISTENCIA:\n"
                        f"Total impresora: {diferencia_total:,} páginas\n"
                        f"Suma usuarios: {suma_consumos:,} páginas\n"
                        f"Diferencia: {diferencia_total - suma_consumos:,} páginas ({diferencia_porcentual*100:.1f}%)\n"
                        f"Posibles causas: impresiones sin autenticación, usuarios borrados"
                    )
                    cierre.notas = (cierre.notas or "") + nota_diferencia
            
            # ====================================================================
            # CALCULAR HASH DE VERIFICACIÓN
            # ====================================================================
            
            hash_data = f"{cierre.printer_id}{cierre.tipo_periodo}{cierre.fecha_inicio}{cierre.fecha_fin}{cierre.total_paginas}{count}"
            cierre.hash_verificacion = hashlib.sha256(hash_data.encode()).hexdigest()
            
            db.commit()
            db.refresh(cierre)
            
            return cierre
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error al crear cierre: {e}")
    
    @staticmethod
    def _calcular_consumo_usuario(
        db: Session,
        printer_id: int,
        codigo_usuario: str,
        fecha_inicio: date,
        fecha_fin: date,
        cierre_anterior: Optional[CierreMensual]
    ) -> Optional[Dict]:
        """
        Calcula el consumo de un usuario en un período
        
        Returns:
            Dict con información del consumo o None si no hay datos
        """
        # Obtener contador más reciente del usuario
        contador_actual = db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == printer_id,
            ContadorUsuario.codigo_usuario == codigo_usuario
        ).order_by(ContadorUsuario.fecha_lectura.desc()).first()
        
        if not contador_actual:
            return None
        
        # Si hay cierre anterior, obtener contador del usuario en ese cierre
        contador_anterior = None
        if cierre_anterior:
            contador_anterior = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == cierre_anterior.id,
                CierreMensualUsuario.codigo_usuario == codigo_usuario
            ).first()
        
        # Calcular consumo
        if contador_anterior:
            # Hay cierre anterior, calcular diferencia
            consumo_total = contador_actual.total_paginas - contador_anterior.total_paginas
            consumo_copiadora = (contador_actual.copiadora_bn + contador_actual.copiadora_todo_color) - \
                               (contador_anterior.copiadora_bn + contador_anterior.copiadora_color)
            consumo_impresora = (contador_actual.impresora_bn + contador_actual.impresora_color) - \
                               (contador_anterior.impresora_bn + contador_anterior.impresora_color)
            consumo_escaner = (contador_actual.escaner_bn + contador_actual.escaner_todo_color) - \
                             (contador_anterior.escaner_bn + contador_anterior.escaner_color)
            consumo_fax = contador_actual.fax_bn - contador_anterior.fax_bn
        else:
            # Primer cierre: buscar contador al inicio del período
            contador_inicio = db.query(ContadorUsuario).filter(
                ContadorUsuario.printer_id == printer_id,
                ContadorUsuario.codigo_usuario == codigo_usuario,
                ContadorUsuario.fecha_lectura >= fecha_inicio,
                ContadorUsuario.fecha_lectura <= fecha_fin
            ).order_by(ContadorUsuario.fecha_lectura.asc()).first()
            
            if contador_inicio and contador_inicio.id != contador_actual.id:
                # Hay contador al inicio del período, calcular diferencia
                consumo_total = contador_actual.total_paginas - contador_inicio.total_paginas
                consumo_copiadora = (contador_actual.copiadora_bn + contador_actual.copiadora_todo_color) - \
                                   (contador_inicio.copiadora_bn + contador_inicio.copiadora_todo_color)
                consumo_impresora = (contador_actual.impresora_bn + contador_actual.impresora_color) - \
                                   (contador_inicio.impresora_bn + contador_inicio.impresora_color)
                consumo_escaner = (contador_actual.escaner_bn + contador_actual.escaner_todo_color) - \
                                 (contador_inicio.escaner_bn + contador_inicio.escaner_todo_color)
                consumo_fax = contador_actual.fax_bn - contador_inicio.fax_bn
            else:
                # Solo hay una lectura en el período, usar el total actual como consumo
                consumo_total = contador_actual.total_paginas
                consumo_copiadora = contador_actual.copiadora_bn + contador_actual.copiadora_todo_color
                consumo_impresora = contador_actual.impresora_bn + contador_actual.impresora_color
                consumo_escaner = contador_actual.escaner_bn + contador_actual.escaner_todo_color
                consumo_fax = contador_actual.fax_bn
        
        return {
            'codigo_usuario': codigo_usuario,
            'nombre_usuario': contador_actual.nombre_usuario,
            'contador_actual': contador_actual.total_paginas,
            'total_bn': contador_actual.total_bn,
            'total_color': contador_actual.total_color,
            'copiadora_bn': contador_actual.copiadora_bn,
            'copiadora_color': contador_actual.copiadora_todo_color,
            'impresora_bn': contador_actual.impresora_bn,
            'impresora_color': contador_actual.impresora_color,
            'escaner_bn': contador_actual.escaner_bn,
            'escaner_color': contador_actual.escaner_todo_color,
            'fax_bn': contador_actual.fax_bn,
            'consumo_total': max(0, consumo_total),
            'consumo_copiadora': max(0, consumo_copiadora),
            'consumo_impresora': max(0, consumo_impresora),
            'consumo_escaner': max(0, consumo_escaner),
            'consumo_fax': max(0, consumo_fax)
        }
    
    @staticmethod
    def close_month_helper(
        db: Session,
        printer_id: int,
        year: int,
        month: int,
        cerrado_por: Optional[str] = None,
        notas: Optional[str] = None
    ) -> CierreMensual:
        """
        Helper para crear cierre mensual (mantiene compatibilidad con código existente)
        """
        # Calcular primer y último día del mes
        fecha_inicio = date(year, month, 1)
        ultimo_dia = calendar.monthrange(year, month)[1]
        fecha_fin = date(year, month, ultimo_dia)
        
        return CloseService.create_close(
            db=db,
            printer_id=printer_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tipo_periodo='mensual',
            cerrado_por=cerrado_por,
            notas=notas,
            validar_secuencia=True
        )
