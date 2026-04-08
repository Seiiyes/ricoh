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
        
        # 6. No se valida que sea inicio de mes ni secuencia - el usuario decide el rango libremente
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
        
        # 8. Nota: La validación de antigüedad se eliminó porque el endpoint
        # ahora lee los contadores automáticamente antes de crear el cierre
        
        # 9. Obtener cierre anterior (el más reciente antes de este período)
        cierre_anterior = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id,
            CierreMensual.fecha_fin < fecha_inicio
        ).order_by(CierreMensual.fecha_fin.desc()).first()
        
        # 10. La validación de secuencia mensual se eliminó para permitir cierres libres
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
            
            # Obtener usuarios únicos por user_id (normalizado)
            usuarios_ids = db.query(ContadorUsuario.user_id).filter(
                ContadorUsuario.printer_id == printer_id,
                ContadorUsuario.user_id.isnot(None)  # Solo usuarios con user_id
            ).distinct().all()
            
            print(f"\n📋 Procesando {len(usuarios_ids)} usuarios únicos...")
            
            for (user_id,) in usuarios_ids:
                consumo = CloseService._calcular_consumo_usuario(
                    db, printer_id, user_id, fecha_inicio, fecha_fin, cierre_anterior
                )
                
                if consumo:
                    usuario_cierre = CierreMensualUsuario(
                        cierre_mensual_id=cierre.id,
                        user_id=consumo['user_id'],  # ← NORMALIZADO
                        
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
            
            print(f"✅ {len(usuarios_snapshot)} usuarios procesados para snapshot")
            
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
        user_id: int,  # ← CAMBIO: ahora recibe user_id en lugar de codigo_usuario
        fecha_inicio: date,
        fecha_fin: date,
        cierre_anterior: Optional[CierreMensual]
    ) -> Optional[Dict]:
        """
        Calcula el consumo de un usuario en un período
        
        Args:
            user_id: ID del usuario (FK a tabla users) - NORMALIZADO
        
        Returns:
            Dict con información del consumo o None si no hay datos
        """
        from sqlalchemy import cast, Date
        
        # Obtener contador más reciente del usuario DENTRO DEL PERÍODO
        fecha_fin_datetime = datetime.combine(fecha_fin, datetime.max.time())
        
        # ← CAMBIO: Buscar por user_id en lugar de codigo_usuario
        contador_actual = db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == printer_id,
            ContadorUsuario.user_id == user_id,
            ContadorUsuario.fecha_lectura <= fecha_fin_datetime
        ).order_by(ContadorUsuario.fecha_lectura.desc()).first()
        
        if not contador_actual:
            return None
        
        # Si hay cierre anterior, obtener contador del usuario en ese cierre
        contador_anterior = None
        if cierre_anterior:
            # ← CAMBIO: Buscar por user_id en lugar de codigo_usuario
            contador_anterior = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == cierre_anterior.id,
                CierreMensualUsuario.user_id == user_id
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
            # ← CAMBIO: Buscar por user_id en lugar de codigo_usuario
            contador_inicio = db.query(ContadorUsuario).filter(
                ContadorUsuario.printer_id == printer_id,
                ContadorUsuario.user_id == user_id,
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
                # Solo hay una lectura en el período, consumo = 0 (no hay referencia anterior)
                consumo_total = 0
                consumo_copiadora = 0
                consumo_impresora = 0
                consumo_escaner = 0
                consumo_fax = 0
        
        return {
            'user_id': user_id,  # ← Retornar user_id
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

    @staticmethod
    def comparar_cierres(
        db: Session,
        cierre_antiguo_id: int,
        cierre_reciente_id: int
    ) -> Dict:
        """
        Compara dos cierres (sin importar si son diarios, semanales o mensuales)
        calculando el consumo (diferencia) tanto general como por usuario.
        
        cierre_antiguo_id: El cierre base (inicial)
        cierre_reciente_id: El cierre final (el más reciente)
        
        Retorna el esquema dict compatible con ComparacionCierresResponse.
        """
        cierre_antiguo = db.query(CierreMensual).filter(CierreMensual.id == cierre_antiguo_id).first()
        cierre_reciente = db.query(CierreMensual).filter(CierreMensual.id == cierre_reciente_id).first()
        
        if not cierre_antiguo:
            raise ValueError(f"Cierre base {cierre_antiguo_id} no encontrado")
        if not cierre_reciente:
            raise ValueError(f"Cierre final {cierre_reciente_id} no encontrado")
            
        if cierre_antiguo.printer_id != cierre_reciente.printer_id:
            raise ValueError("Los cierres pertenecen a impresoras diferentes.")
            
        if cierre_antiguo.fecha_fin >= cierre_reciente.fecha_inicio:
            # Aunque la validación estricta exigiría cierre_antiguo.fecha_fin < cierre_reciente.fecha_fin
            # Es importante advertir pero quizas no bloquear si son solapados,
            # pero por lógica antigua vs reciente:
            if cierre_antiguo.fecha_cierre >= cierre_reciente.fecha_cierre:
                # Intercambiar si están al revés
                cierre_antiguo, cierre_reciente = cierre_reciente, cierre_antiguo

        # Diferencia de totales del equipo (puede ser negativa si hay correcciones)
        diferencia_total = cierre_reciente.total_paginas - cierre_antiguo.total_paginas
        diferencia_copiadora = cierre_reciente.total_copiadora - cierre_antiguo.total_copiadora
        diferencia_impresora = cierre_reciente.total_impresora - cierre_antiguo.total_impresora
        diferencia_escaner = cierre_reciente.total_escaner - cierre_antiguo.total_escaner
        diferencia_fax = cierre_reciente.total_fax - cierre_antiguo.total_fax
        
        # Diferencia de días
        dias_entre_cierres = (cierre_reciente.fecha_cierre.date() - cierre_antiguo.fecha_cierre.date()).days
        
        # Comparación de usuarios
        # 1. Armar mapa de usuarios de ambos cierres por user_id (normalizado)
        usuarios_antiguos = {u.user_id: u for u in cierre_antiguo.usuarios if u.user_id}
        usuarios_recientes = {u.user_id: u for u in cierre_reciente.usuarios if u.user_id}
        
        user_ids_unicos = set(usuarios_antiguos.keys()).union(set(usuarios_recientes.keys()))
        
        usuarios_comparacion = []
        for user_id in user_ids_unicos:
            u_antiguo = usuarios_antiguos.get(user_id)
            u_reciente = usuarios_recientes.get(user_id)
            
            # Obtener información del usuario desde la tabla users
            from db.models import User
            user = db.query(User).filter(User.id == user_id).first()
            codigo = user.codigo_de_usuario if user else str(user_id)
            nombre = user.name if user else f"Usuario {user_id}"
            
            # Contadores acumulados
            total_c1 = u_antiguo.total_paginas if u_antiguo else 0
            total_c2 = u_reciente.total_paginas if u_reciente else 0
            
            # B/N y Color acumulados
            bn_c1 = u_antiguo.total_bn if u_antiguo else 0
            bn_c2 = u_reciente.total_bn if u_reciente else 0
            color_c1 = u_antiguo.total_color if u_antiguo else 0
            color_c2 = u_reciente.total_color if u_reciente else 0
            
            # Diferencia (puede ser negativa si hay correcciones)
            diferencia = total_c2 - total_c1
            diferencia_bn = bn_c2 - bn_c1
            diferencia_color = color_c2 - color_c1
            
            porcentaje_cambio = 0.0
            if total_c1 > 0:
                porcentaje_cambio = round((diferencia / total_c1) * 100, 2)
            else:
                porcentaje_cambio = 100.0 if diferencia > 0 else 0.0
                
            usuario_data = {
                "codigo_usuario": codigo,
                "nombre_usuario": nombre,
                "consumo_cierre1": total_c1,
                "consumo_cierre2": total_c2,
                "diferencia": diferencia,
                "diferencia_bn": diferencia_bn,
                "diferencia_color": diferencia_color,
                "porcentaje_cambio": porcentaje_cambio,
                
                "total_paginas_cierre1": total_c1,
                "total_paginas_cierre2": total_c2,
                
                "consumo_copiadora_cierre1": (u_antiguo.copiadora_bn + u_antiguo.copiadora_color) if u_antiguo else 0,
                "consumo_impresora_cierre1": (u_antiguo.impresora_bn + u_antiguo.impresora_color) if u_antiguo else 0,
                "consumo_escaner_cierre1": (u_antiguo.escaner_bn + u_antiguo.escaner_color) if u_antiguo else 0,
                "consumo_fax_cierre1": u_antiguo.fax_bn if u_antiguo else 0,
                
                "consumo_copiadora_cierre2": (u_reciente.copiadora_bn + u_reciente.copiadora_color) if u_reciente else 0,
                "consumo_impresora_cierre2": (u_reciente.impresora_bn + u_reciente.impresora_color) if u_reciente else 0,
                "consumo_escaner_cierre2": (u_reciente.escaner_bn + u_reciente.escaner_color) if u_reciente else 0,
                "consumo_fax_cierre2": u_reciente.fax_bn if u_reciente else 0,
                
                # Desglose B/N y Color para cierre 1
                "copiadora_bn_cierre1": u_antiguo.copiadora_bn if u_antiguo else 0,
                "copiadora_color_cierre1": u_antiguo.copiadora_color if u_antiguo else 0,
                "impresora_bn_cierre1": u_antiguo.impresora_bn if u_antiguo else 0,
                "impresora_color_cierre1": u_antiguo.impresora_color if u_antiguo else 0,
                "escaner_bn_cierre1": u_antiguo.escaner_bn if u_antiguo else 0,
                "escaner_color_cierre1": u_antiguo.escaner_color if u_antiguo else 0,
                
                # Desglose B/N y Color para cierre 2
                "copiadora_bn_cierre2": u_reciente.copiadora_bn if u_reciente else 0,
                "copiadora_color_cierre2": u_reciente.copiadora_color if u_reciente else 0,
                "impresora_bn_cierre2": u_reciente.impresora_bn if u_reciente else 0,
                "impresora_color_cierre2": u_reciente.impresora_color if u_reciente else 0,
                "escaner_bn_cierre2": u_reciente.escaner_bn if u_reciente else 0,
                "escaner_color_cierre2": u_reciente.escaner_color if u_reciente else 0,
            }
            usuarios_comparacion.append(usuario_data)
            
        # Separar en listas de aumento y disminución
        usuarios_comparacion = sorted(usuarios_comparacion, key=lambda x: x['diferencia'], reverse=True)
        top_aumento = [u for u in usuarios_comparacion if u['diferencia'] > 0]
        top_disminucion = [u for u in usuarios_comparacion if u['diferencia'] <= 0]
        
        activos = len([u for u in usuarios_comparacion if u['diferencia'] != 0])
        promedio = diferencia_total / activos if activos > 0 else 0
        
        # Obtener información de la impresora
        from db.models import Printer
        printer = db.query(Printer).filter(Printer.id == cierre_antiguo.printer_id).first()
        
        return {
            "cierre1": cierre_antiguo,
            "cierre2": cierre_reciente,
            "printer": {
                "id": printer.id,
                "hostname": printer.hostname,
                "ip_address": printer.ip_address,
                "location": printer.location,
                "serial_number": printer.serial_number,
                "has_color": printer.has_color,
                "has_scanner": printer.has_scanner,
                "has_fax": printer.has_fax,
            } if printer else None,
            "diferencia_total": diferencia_total,
            "diferencia_copiadora": diferencia_copiadora,
            "diferencia_impresora": diferencia_impresora,
            "diferencia_escaner": diferencia_escaner,
            "diferencia_fax": diferencia_fax,
            "dias_entre_cierres": abs(dias_entre_cierres),
            "top_usuarios_aumento": top_aumento,
            "top_usuarios_disminucion": top_disminucion,
            "total_usuarios_activos": activos,
            "promedio_consumo_por_usuario": round(promedio, 2)
        }

    @staticmethod
    def create_close_all_printers(
        db: Session,
        fecha_inicio: date,
        fecha_fin: date,
        tipo_periodo: str = 'personalizado',
        cerrado_por: Optional[str] = None,
        notas: Optional[str] = None,
        empresa_id: Optional[int] = None
    ) -> Dict:
        """
        Crea cierres para todas las impresoras activas simultáneamente
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            tipo_periodo: Tipo de período ('diario', 'semanal', 'mensual', 'personalizado')
            cerrado_por: Usuario que realiza el cierre
            notas: Notas adicionales
            empresa_id: ID de empresa para filtrar impresoras (opcional)
            
        Returns:
            Dict con estadísticas de cierres creados
        """
        # Obtener todas las impresoras activas
        query = db.query(Printer).filter(Printer.status != 'offline')
        
        # Filtrar por empresa si se especifica
        if empresa_id:
            query = query.filter(Printer.empresa_id == empresa_id)
        
        printers = query.all()
        
        if not printers:
            return {
                "success": True,
                "message": "No hay impresoras disponibles",
                "successful": 0,
                "failed": 0,
                "total": 0,
                "results": []
            }
        
        results = []
        successful = 0
        failed = 0
        
        for printer in printers:
            try:
                # Crear cierre para esta impresora
                cierre = CloseService.create_close(
                    db=db,
                    printer_id=printer.id,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    tipo_periodo=tipo_periodo,
                    cerrado_por=cerrado_por,
                    notas=notas,
                    validar_secuencia=False  # No validar secuencia en cierres masivos
                )
                
                results.append({
                    "printer_id": printer.id,
                    "printer_name": printer.hostname,
                    "success": True,
                    "cierre_id": cierre.id,
                    "total_paginas": cierre.total_paginas,
                    "usuarios_count": len(cierre.usuarios),
                    "error": None
                })
                successful += 1
                
            except Exception as e:
                results.append({
                    "printer_id": printer.id,
                    "printer_name": printer.hostname,
                    "success": False,
                    "cierre_id": None,
                    "total_paginas": 0,
                    "usuarios_count": 0,
                    "error": str(e)
                })
                failed += 1
        
        return {
            "success": True,
            "message": f"Cierres completados: {successful} exitosos, {failed} fallidos",
            "successful": successful,
            "failed": failed,
            "total": len(printers),
            "results": results
        }
