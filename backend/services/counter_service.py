#!/usr/bin/env python3
"""
Counter Service - Servicio de lectura y almacenamiento de contadores
Integra los parsers con la base de datos
"""
import sys
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

# Agregar el directorio backend al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import Printer, ContadorImpresora, ContadorUsuario, CierreMensual, CierreMensualUsuario
from db.database import get_db
from sqlalchemy import func

# Importar parsers
from parsear_contadores import get_printer_counters
from parsear_contadores_usuario import get_all_user_counters
from parsear_contador_ecologico import get_all_eco_users


class CounterService:
    """Servicio para lectura y almacenamiento de contadores"""
    
    @staticmethod
    def validate_counter_data(counters: Dict) -> None:
        """
        Valida que los datos de contadores sean consistentes
        
        Args:
            counters: Dict con datos de contadores
            
        Raises:
            ValueError: Si los datos son inconsistentes
        """
        if counters is None:
            raise ValueError("Datos de contadores son None")
        
        if not isinstance(counters, dict):
            raise ValueError(f"Datos de contadores tienen tipo inválido: {type(counters)}")
        
        # Validar campos requeridos
        required_fields = ['total', 'copiadora', 'impresora', 'fax', 'enviar_total', 
                          'transmision_fax', 'envio_escaner', 'otras_funciones']
        
        for field in required_fields:
            if field not in counters:
                raise ValueError(f"Campo requerido '{field}' no encontrado en contadores")
        
        # Validar que los valores sean numéricos
        if not isinstance(counters['total'], int):
            raise ValueError(f"Campo 'total' debe ser int, es {type(counters['total'])}")
        
        # Validar consistencia: total debe ser >= suma de copiadora + impresora
        suma_minima = (
            counters['copiadora'].get('blanco_negro', 0) +
            counters['copiadora'].get('color', 0) +
            counters['impresora'].get('blanco_negro', 0) +
            counters['impresora'].get('color', 0)
        )
        
        # Permitir total=0 solo si todos los contadores son 0
        if counters['total'] == 0 and suma_minima > 0:
            raise ValueError(
                f"Inconsistencia: total=0 pero suma de contadores={suma_minima}. "
                "Los datos del parser son incorrectos."
            )
        
        # Advertencia si el total es menor que la suma (puede pasar en algunos modelos)
        if counters['total'] > 0 and counters['total'] < suma_minima:
            # No lanzar error, solo advertencia en logs
            # Algunos modelos de impresoras pueden tener esta inconsistencia
            pass
    
    @staticmethod
    def validate_user_counter_data(user: Dict, tipo: str) -> None:
        """
        Valida que los datos de contador de usuario sean consistentes
        
        Args:
            user: Dict con datos de usuario
            tipo: "usuario" o "ecologico"
            
        Raises:
            ValueError: Si los datos son inconsistentes
        """
        if user is None:
            raise ValueError("Datos de usuario son None")
        
        if not isinstance(user, dict):
            raise ValueError(f"Datos de usuario tienen tipo inválido: {type(user)}")
        
        # Validar campos requeridos comunes
        if 'codigo_usuario' not in user:
            raise ValueError("Campo 'codigo_usuario' no encontrado")
        
        if 'nombre_usuario' not in user:
            raise ValueError("Campo 'nombre_usuario' no encontrado")
        
        # Validar según tipo
        if tipo == "usuario":
            if 'total_paginas' not in user:
                raise ValueError("Campo 'total_paginas' no encontrado en contador usuario")
            
            if not isinstance(user['total_paginas'], int):
                raise ValueError(f"Campo 'total_paginas' debe ser int, es {type(user['total_paginas'])}")
        
        elif tipo == "ecologico":
            if 'total_paginas_actual' not in user:
                raise ValueError("Campo 'total_paginas_actual' no encontrado en contador ecológico")
            
            if not isinstance(user['total_paginas_actual'], int):
                raise ValueError(f"Campo 'total_paginas_actual' debe ser int, es {type(user['total_paginas_actual'])}")
    
    @staticmethod
    def read_printer_counters(db: Session, printer_id: int) -> Optional[ContadorImpresora]:
        """
        Lee y guarda contadores totales de una impresora
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            
        Returns:
            ContadorImpresora creado o None si hay error
        """
        # Obtener impresora
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            raise ValueError(f"Impresora con ID {printer_id} no encontrada")
        
        try:
            # Leer contadores usando el parser
            counters = get_printer_counters(printer.ip_address)
            
            # Validar datos antes de guardar
            CounterService.validate_counter_data(counters)
            
            # Crear registro en base de datos
            contador = ContadorImpresora(
                printer_id=printer_id,
                total=counters['total'],
                
                # Copiadora
                copiadora_bn=counters['copiadora']['blanco_negro'],
                copiadora_color=counters['copiadora']['color'],
                copiadora_color_personalizado=counters['copiadora']['color_personalizado'],
                copiadora_dos_colores=counters['copiadora']['dos_colores'],
                
                # Impresora
                impresora_bn=counters['impresora']['blanco_negro'],
                impresora_color=counters['impresora']['color'],
                impresora_color_personalizado=counters['impresora']['color_personalizado'],
                impresora_dos_colores=counters['impresora']['dos_colores'],
                
                # Fax
                fax_bn=counters['fax']['blanco_negro'],
                
                # Enviar/TX Total
                enviar_total_bn=counters['enviar_total']['blanco_negro'],
                enviar_total_color=counters['enviar_total']['color'],
                
                # Transmisión por fax
                transmision_fax_total=counters['transmision_fax']['total'],
                
                # Envío por escáner
                envio_escaner_bn=counters['envio_escaner']['blanco_negro'],
                envio_escaner_color=counters['envio_escaner']['color'],
                
                # Otras funciones
                otras_a3_dlt=counters['otras_funciones']['a3_dlt'],
                otras_duplex=counters['otras_funciones']['duplex'],
                
                fecha_lectura=datetime.now()
            )
            
            db.add(contador)
            db.commit()
            db.refresh(contador)
            
            return contador
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error al leer contadores de impresora {printer_id}: {e}")
    
    @staticmethod
    def read_user_counters(db: Session, printer_id: int) -> List[ContadorUsuario]:
        """
        Lee y guarda contadores por usuario de una impresora
        Detecta automáticamente si usar getUserCounter o getEcoCounter
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            
        Returns:
            Lista de ContadorUsuario creados
        """
        # Obtener impresora
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            raise ValueError(f"Impresora con ID {printer_id} no encontrada")
        
        try:
            contadores_creados = []
            
            # Determinar qué tipo de contador usar
            if printer.tiene_contador_usuario and not printer.usar_contador_ecologico:
                # Usar contador por usuario estándar
                users = get_all_user_counters(printer.ip_address)
                tipo_contador = "usuario"
                
                # Validar que retornó una lista
                if not isinstance(users, list):
                    raise ValueError(f"get_all_user_counters retornó tipo inválido: {type(users)}")
                
                for user in users:
                    # Validar datos del usuario
                    CounterService.validate_user_counter_data(user, tipo_contador)
                    
                    contador = ContadorUsuario(
                        printer_id=printer_id,
                        codigo_usuario=user['codigo_usuario'],
                        nombre_usuario=user['nombre_usuario'],
                        
                        # Totales
                        total_paginas=user['total_paginas'],
                        total_bn=user['total_impresiones']['bn'],
                        total_color=user['total_impresiones']['color'],
                        
                        # Copiadora
                        copiadora_bn=user['copiadora']['blanco_negro'],
                        copiadora_mono_color=user['copiadora']['mono_color'],
                        copiadora_dos_colores=user['copiadora']['dos_colores'],
                        copiadora_todo_color=user['copiadora']['todo_color'],
                        copiadora_hojas_2_caras=user['copiadora'].get('hojas_2_caras', 0),
                        copiadora_paginas_combinadas=user['copiadora'].get('paginas_combinadas', 0),
                        
                        # Impresora
                        impresora_bn=user['impresora']['blanco_negro'],
                        impresora_mono_color=user['impresora']['mono_color'],
                        impresora_dos_colores=user['impresora']['dos_colores'],
                        impresora_color=user['impresora']['color'],
                        impresora_hojas_2_caras=user['impresora'].get('hojas_2_caras', 0),
                        impresora_paginas_combinadas=user['impresora'].get('paginas_combinadas', 0),
                        
                        # Escáner
                        escaner_bn=user['escaner']['blanco_negro'],
                        escaner_todo_color=user['escaner']['todo_color'],
                        
                        # Fax
                        fax_bn=user['fax']['blanco_negro'],
                        fax_paginas_transmitidas=user['fax']['paginas_transmitidas'],
                        
                        # Revelado
                        revelado_negro=user['revelado']['negro'],
                        revelado_color_ymc=user['revelado']['color_ymc'],
                        
                        tipo_contador=tipo_contador,
                        fecha_lectura=datetime.now()
                    )
                    
                    db.add(contador)
                    contadores_creados.append(contador)
                    
            elif printer.usar_contador_ecologico:
                # Usar contador ecológico
                data = get_all_eco_users(printer.ip_address)
                tipo_contador = "ecologico"
                
                # Validar estructura de datos
                if not isinstance(data, dict) or 'users' not in data:
                    raise ValueError("get_all_eco_users retornó estructura inválida")
                
                users = data['users']
                
                if not isinstance(users, list):
                    raise ValueError(f"users no es una lista: {type(users)}")
                
                for user in users:
                    # Validar datos del usuario
                    CounterService.validate_user_counter_data(user, tipo_contador)
                    
                    contador = ContadorUsuario(
                        printer_id=printer_id,
                        codigo_usuario=user['codigo_usuario'],
                        nombre_usuario=user['nombre_usuario'],
                        
                        # Totales (solo tenemos total_paginas_actual)
                        total_paginas=user['total_paginas_actual'],
                        total_bn=0,  # No disponible en contador ecológico
                        total_color=0,  # No disponible en contador ecológico
                        
                        # Métricas ecológicas
                        eco_uso_2_caras=user['uso_2_caras_actual'],
                        eco_uso_combinar=user['uso_combinar_actual'],
                        eco_reduccion_papel=user['reduccion_papel_actual'],
                        
                        tipo_contador=tipo_contador,
                        fecha_lectura=datetime.now()
                    )
                    
                    db.add(contador)
                    contadores_creados.append(contador)
            else:
                raise ValueError(f"Impresora {printer_id} no tiene contador por usuario configurado")
            
            db.commit()
            
            # Refresh todos los contadores
            for contador in contadores_creados:
                db.refresh(contador)
            
            return contadores_creados
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Error al leer contadores de usuarios de impresora {printer_id}: {e}")
    
    @staticmethod
    def close_month(db: Session, printer_id: int, year: int, month: int, 
                   cerrado_por: Optional[str] = None, notas: Optional[str] = None) -> CierreMensual:
        """
        Realiza cierre mensual de contadores con snapshot de usuarios
        
        NOTA: Este método es un wrapper del nuevo sistema unificado de cierres.
        Para más flexibilidad, usar CloseService.create_close()
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            year: Año del cierre
            month: Mes del cierre (1-12)
            cerrado_por: Usuario que realiza el cierre
            notas: Notas adicionales
            
        Returns:
            CierreMensual creado con usuarios
            
        Raises:
            ValueError: Si hay errores de validación
        """
        from services.close_service import CloseService
        return CloseService.close_month_helper(db, printer_id, year, month, cerrado_por, notas)
    
    @staticmethod
    def _calcular_consumo_usuario(db: Session, printer_id: int, codigo_usuario: str, 
                                  year: int, month: int, cierre_anterior: Optional[CierreMensual]) -> Optional[Dict]:
        """
        Calcula el consumo mensual de un usuario
        
        Returns:
            Dict con datos del usuario y consumo, o None si no hay datos
        """
        from datetime import datetime
        import calendar
        
        # Última lectura del mes actual
        fecha_fin_mes = datetime(
            year, 
            month, 
            calendar.monthrange(year, month)[1], 
            23, 59, 59
        )
        
        lectura_actual = db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == printer_id,
            ContadorUsuario.codigo_usuario == codigo_usuario,
            ContadorUsuario.created_at <= fecha_fin_mes
        ).order_by(ContadorUsuario.created_at.desc()).first()
        
        if not lectura_actual:
            return None
        
        # Última lectura del mes anterior
        lectura_anterior = None
        if cierre_anterior:
            if month > 1:
                mes_anterior = month - 1
                anio_anterior = year
            else:
                mes_anterior = 12
                anio_anterior = year - 1
            
            fecha_fin_mes_anterior = datetime(
                anio_anterior,
                mes_anterior,
                calendar.monthrange(anio_anterior, mes_anterior)[1],
                23, 59, 59
            )
            
            lectura_anterior = db.query(ContadorUsuario).filter(
                ContadorUsuario.printer_id == printer_id,
                ContadorUsuario.codigo_usuario == codigo_usuario,
                ContadorUsuario.created_at <= fecha_fin_mes_anterior
            ).order_by(ContadorUsuario.created_at.desc()).first()
        
        # Calcular consumos
        if lectura_anterior:
            consumo_total = lectura_actual.total_paginas - lectura_anterior.total_paginas
            consumo_copiadora = (lectura_actual.copiadora_bn + lectura_actual.copiadora_todo_color) - \
                               (lectura_anterior.copiadora_bn + lectura_anterior.copiadora_todo_color)
            consumo_impresora = (lectura_actual.impresora_bn + lectura_actual.impresora_color) - \
                               (lectura_anterior.impresora_bn + lectura_anterior.impresora_color)
            consumo_escaner = (lectura_actual.escaner_bn + lectura_actual.escaner_todo_color) - \
                             (lectura_anterior.escaner_bn + lectura_anterior.escaner_todo_color)
            consumo_fax = lectura_actual.fax_bn - lectura_anterior.fax_bn
        else:
            # Primer cierre, consumo = 0
            consumo_total = 0
            consumo_copiadora = 0
            consumo_impresora = 0
            consumo_escaner = 0
            consumo_fax = 0
        
        return {
            'codigo_usuario': lectura_actual.codigo_usuario,
            'nombre_usuario': lectura_actual.nombre_usuario,
            'contador_actual': lectura_actual.total_paginas,
            'total_bn': lectura_actual.total_bn,
            'total_color': lectura_actual.total_color,
            'copiadora_bn': lectura_actual.copiadora_bn,
            'copiadora_color': lectura_actual.copiadora_todo_color,
            'impresora_bn': lectura_actual.impresora_bn,
            'impresora_color': lectura_actual.impresora_color,
            'escaner_bn': lectura_actual.escaner_bn,
            'escaner_color': lectura_actual.escaner_todo_color,
            'fax_bn': lectura_actual.fax_bn,
            'consumo_total': consumo_total,
            'consumo_copiadora': consumo_copiadora,
            'consumo_impresora': consumo_impresora,
            'consumo_escaner': consumo_escaner,
            'consumo_fax': consumo_fax
        }
    
    @staticmethod
    def read_all_printers(db: Session) -> Dict[int, Dict]:
        """
        Lee contadores de todas las impresoras activas
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Dict con resultados por impresora
        """
        # Obtener todas las impresoras
        printers = db.query(Printer).all()
        
        results = {}
        
        for printer in printers:
            result = {
                'printer_id': printer.id,
                'hostname': printer.hostname,
                'ip_address': printer.ip_address,
                'success': False,
                'contador_total': None,
                'contadores_usuarios': [],
                'error': None
            }
            
            try:
                # Leer contador total
                contador_total = CounterService.read_printer_counters(db, printer.id)
                result['contador_total'] = contador_total
                result['success'] = True
                
                # Leer contadores por usuario (si está configurado)
                if printer.tiene_contador_usuario or printer.usar_contador_ecologico:
                    try:
                        contadores_usuarios = CounterService.read_user_counters(db, printer.id)
                        result['contadores_usuarios'] = contadores_usuarios
                    except Exception as e:
                        result['error'] = f"Error al leer usuarios: {e}"
                        
            except Exception as e:
                result['error'] = str(e)
            
            results[printer.id] = result
        
        return results
    
    @staticmethod
    def get_latest_counter(db: Session, printer_id: int) -> Optional[ContadorImpresora]:
        """
        Obtiene el último contador registrado de una impresora
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            
        Returns:
            ContadorImpresora más reciente o None
        """
        return db.query(ContadorImpresora).filter(
            ContadorImpresora.printer_id == printer_id
        ).order_by(ContadorImpresora.fecha_lectura.desc()).first()
    
    @staticmethod
    def get_user_counters_latest(db: Session, printer_id: int) -> List[ContadorUsuario]:
        """
        Obtiene los últimos contadores por usuario de una impresora
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            
        Returns:
            Lista de ContadorUsuario más recientes
        """
        # Obtener el created_at de la última lectura
        # Usamos created_at en lugar de fecha_lectura porque todos los registros
        # de una misma sesión de lectura tienen el mismo created_at
        latest = db.query(ContadorUsuario.created_at).filter(
            ContadorUsuario.printer_id == printer_id
        ).order_by(ContadorUsuario.created_at.desc()).first()
        
        if not latest:
            return []
        
        # Obtener todos los contadores de esa sesión de lectura
        return db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == printer_id,
            ContadorUsuario.created_at == latest[0]
        ).all()
    
    @staticmethod
    def get_monthly_closes(db: Session, printer_id: int, year: Optional[int] = None) -> List[CierreMensual]:
        """
        Obtiene los cierres mensuales de una impresora
        
        Args:
            db: Sesión de base de datos
            printer_id: ID de la impresora
            year: Año (opcional, si no se especifica trae todos)
            
        Returns:
            Lista de CierreMensual
        """
        query = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id
        )
        
        if year:
            query = query.filter(CierreMensual.anio == year)
        
        return query.order_by(CierreMensual.anio, CierreMensual.mes).all()


# Funciones de conveniencia para uso directo
def read_printer_counters(printer_id: int) -> Optional[ContadorImpresora]:
    """Función de conveniencia para leer contadores de impresora"""
    db = next(get_db())
    try:
        return CounterService.read_printer_counters(db, printer_id)
    finally:
        db.close()


def read_user_counters(printer_id: int) -> List[ContadorUsuario]:
    """Función de conveniencia para leer contadores de usuarios"""
    db = next(get_db())
    try:
        return CounterService.read_user_counters(db, printer_id)
    finally:
        db.close()


def close_month(printer_id: int, year: int, month: int, 
                cerrado_por: Optional[str] = None, notas: Optional[str] = None) -> CierreMensual:
    """Función de conveniencia para realizar cierre mensual"""
    db = next(get_db())
    try:
        return CounterService.close_month(db, printer_id, year, month, cerrado_por, notas)
    finally:
        db.close()


def read_all_printers() -> Dict[int, Dict]:
    """Función de conveniencia para leer todas las impresoras"""
    db = next(get_db())
    try:
        return CounterService.read_all_printers(db)
    finally:
        db.close()

