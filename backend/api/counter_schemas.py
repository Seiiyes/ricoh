"""
Pydantic schemas for Counter API endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# Import printer schemas for capabilities
from .schemas import PrinterResponse, CapabilitiesResponse


# ============================================================================
# Counter Schemas
# ============================================================================

class ContadorImpresoraResponse(BaseModel):
    """Response schema for printer counter"""
    id: int
    printer_id: int
    total: int
    
    # Copiadora
    copiadora_bn: int
    copiadora_color: int
    copiadora_color_personalizado: int
    copiadora_dos_colores: int
    
    # Impresora
    impresora_bn: int
    impresora_color: int
    impresora_color_personalizado: int
    impresora_dos_colores: int
    
    # Fax
    fax_bn: int
    
    # Enviar/TX Total
    enviar_total_bn: int
    enviar_total_color: int
    
    # Transmisión por fax
    transmision_fax_total: int
    
    # Envío por escáner
    envio_escaner_bn: int
    envio_escaner_color: int
    
    # Otras funciones
    otras_a3_dlt: int
    otras_duplex: int
    
    # Metadata
    fecha_lectura: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContadorUsuarioResponse(BaseModel):
    """Response schema for user counter"""
    id: int
    printer_id: int
    codigo_usuario: str
    nombre_usuario: str
    
    # Totales
    total_paginas: int
    total_bn: int
    total_color: int
    
    # Copiadora
    copiadora_bn: int
    copiadora_mono_color: int
    copiadora_dos_colores: int
    copiadora_todo_color: int
    copiadora_hojas_2_caras: int
    copiadora_paginas_combinadas: int
    
    # Impresora
    impresora_bn: int
    impresora_mono_color: int
    impresora_dos_colores: int
    impresora_color: int
    impresora_hojas_2_caras: int
    impresora_paginas_combinadas: int
    
    # Escáner
    escaner_bn: int
    escaner_todo_color: int
    
    # Fax
    fax_bn: int
    fax_paginas_transmitidas: int
    
    # Revelado
    revelado_negro: int
    revelado_color_ymc: int
    
    # Métricas ecológicas
    eco_uso_2_caras: Optional[str]
    eco_uso_combinar: Optional[str]
    eco_reduccion_papel: Optional[str]
    
    # Tipo
    tipo_contador: str
    
    # Metadata
    fecha_lectura: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class CierreMensualResponse(BaseModel):
    """Response schema for monthly close"""
    id: int
    printer_id: int
    
    # Tipo y período (agregado en migración 008)
    tipo_periodo: str  # diario, semanal, mensual, personalizado
    fecha_inicio: date
    fecha_fin: date
    
    # Período (mantener para compatibilidad)
    anio: int
    mes: int
    
    # Totales
    total_paginas: int
    total_copiadora: int
    total_impresora: int
    total_escaner: int
    total_fax: int
    
    # Diferencias
    diferencia_total: int
    diferencia_copiadora: int
    diferencia_impresora: int
    diferencia_escaner: int
    diferencia_fax: int
    
    # Metadata
    fecha_cierre: datetime
    cerrado_por: Optional[str]
    notas: Optional[str]
    hash_verificacion: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CierreRequest(BaseModel):
    """Request schema for creating any type of close"""
    printer_id: int = Field(..., gt=0, description="ID de la impresora")
    tipo_periodo: str = Field(..., description="Tipo de período: diario, semanal, mensual, personalizado")
    fecha_inicio: date = Field(..., description="Fecha de inicio del período")
    fecha_fin: date = Field(..., description="Fecha de fin del período")
    cerrado_por: Optional[str] = Field(None, max_length=100, description="Usuario que realiza el cierre")
    notas: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")
    
    @validator('tipo_periodo')
    def validate_tipo_periodo(cls, v):
        tipos_validos = ['diario', 'semanal', 'mensual', 'personalizado']
        if v not in tipos_validos:
            raise ValueError(f'tipo_periodo debe ser uno de: {", ".join(tipos_validos)}')
        return v
    
    @validator('fecha_fin')
    def validate_fechas(cls, v, values):
        if 'fecha_inicio' in values and v < values['fecha_inicio']:
            raise ValueError('fecha_fin debe ser mayor o igual a fecha_inicio')
        return v


class CierreMensualRequest(BaseModel):
    """Request schema for creating monthly close"""
    printer_id: int = Field(..., gt=0, description="ID de la impresora")
    anio: int = Field(..., ge=2020, le=2100, description="Año del cierre")
    mes: int = Field(..., ge=1, le=12, description="Mes del cierre (1-12)")
    cerrado_por: Optional[str] = Field(None, max_length=100, description="Usuario que realiza el cierre")
    notas: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")


class ReadCounterResponse(BaseModel):
    """Response schema for read counter operation"""
    success: bool
    printer_id: int
    contador_total: Optional[ContadorImpresoraResponse]
    usuarios_count: int
    error: Optional[str]


class ReadAllCountersResponse(BaseModel):
    """Response schema for read all counters operation"""
    success: bool
    total_printers: int
    successful: int
    failed: int
    results: List[ReadCounterResponse]


class CounterHistoryQuery(BaseModel):
    """Query parameters for counter history"""
    start_date: Optional[datetime] = Field(None, description="Fecha inicial")
    end_date: Optional[datetime] = Field(None, description="Fecha final")
    limit: int = Field(100, ge=1, le=1000, description="Límite de registros")


class UserCounterHistoryQuery(BaseModel):
    """Query parameters for user counter history"""
    codigo_usuario: Optional[str] = Field(None, max_length=8, description="Código de usuario")
    start_date: Optional[datetime] = Field(None, description="Fecha inicial")
    end_date: Optional[datetime] = Field(None, description="Fecha final")
    limit: int = Field(100, ge=1, le=1000, description="Límite de registros")



# ============================================================================
# Monthly Close User Snapshot Schemas
# ============================================================================

class CierreMensualUsuarioResponse(BaseModel):
    """Response schema for monthly close user snapshot"""
    id: int
    cierre_mensual_id: int
    codigo_usuario: str
    nombre_usuario: str
    
    # Contadores al cierre
    total_paginas: int
    total_bn: int
    total_color: int
    
    # Desglose por función
    copiadora_bn: int
    copiadora_color: int
    impresora_bn: int
    impresora_color: int
    escaner_bn: int
    escaner_color: int
    fax_bn: int
    
    # Consumo del mes
    consumo_total: int
    consumo_copiadora: int
    consumo_impresora: int
    consumo_escaner: int
    consumo_fax: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class CierreMensualDetalleResponse(BaseModel):
    """Response schema for monthly close with user details"""
    id: int
    printer_id: int
    anio: int
    mes: int
    
    # Totales
    total_paginas: int
    total_copiadora: int
    total_impresora: int
    total_escaner: int
    total_fax: int
    
    # Diferencias
    diferencia_total: int
    diferencia_copiadora: int
    diferencia_impresora: int
    diferencia_escaner: int
    diferencia_fax: int
    
    # Metadata
    fecha_cierre: datetime
    fecha_inicio: date
    fecha_fin: date
    cerrado_por: Optional[str]
    notas: Optional[str]
    hash_verificacion: Optional[str]
    created_at: datetime
    
    # Printer info with capabilities
    printer: Optional[PrinterResponse] = None
    
    # Usuarios del cierre (paginados)
    usuarios: List[CierreMensualUsuarioResponse]
    
    # Paginación
    total_usuarios: int = 0
    page: int = 1
    page_size: int = 50
    total_pages: int = 1
    
    class Config:
        from_attributes = True



# ============================================================================
# Comparison Schemas
# ============================================================================

class UsuarioComparacion(BaseModel):
    """Usuario con comparación entre dos cierres
    
    Contiene todos los usuarios sin límite artificial.
    """
    codigo_usuario: str
    nombre_usuario: str
    consumo_cierre1: int
    consumo_cierre2: int
    diferencia: int
    porcentaje_cambio: float
    
    # Campos opcionales para vista detallada
    total_paginas_cierre1: Optional[int] = None  # Contador acumulado en cierre 1
    total_paginas_cierre2: Optional[int] = None  # Contador acumulado en cierre 2
    
    # Desglose del consumo en cierre 1
    consumo_copiadora_cierre1: Optional[int] = None
    consumo_impresora_cierre1: Optional[int] = None
    consumo_escaner_cierre1: Optional[int] = None
    consumo_fax_cierre1: Optional[int] = None
    
    # Desglose del consumo en cierre 2
    consumo_copiadora_cierre2: Optional[int] = None
    consumo_impresora_cierre2: Optional[int] = None
    consumo_escaner_cierre2: Optional[int] = None
    consumo_fax_cierre2: Optional[int] = None
    
    # Desglose B/N y Color para cierre 1
    copiadora_bn_cierre1: Optional[int] = None
    copiadora_color_cierre1: Optional[int] = None
    impresora_bn_cierre1: Optional[int] = None
    impresora_color_cierre1: Optional[int] = None
    escaner_bn_cierre1: Optional[int] = None
    escaner_color_cierre1: Optional[int] = None
    
    # Desglose B/N y Color para cierre 2
    copiadora_bn_cierre2: Optional[int] = None
    copiadora_color_cierre2: Optional[int] = None
    impresora_bn_cierre2: Optional[int] = None
    impresora_color_cierre2: Optional[int] = None
    escaner_bn_cierre2: Optional[int] = None
    escaner_color_cierre2: Optional[int] = None


class ComparacionCierresResponse(BaseModel):
    """Response schema for comparing two closes
    
    Retorna todos los usuarios sin límite artificial.
    """
    cierre1: CierreMensualResponse
    cierre2: CierreMensualResponse
    
    # Información de la impresora
    printer: Optional[Dict[str, Any]] = None
    
    # Diferencias de totales
    diferencia_total: int
    diferencia_copiadora: int
    diferencia_impresora: int
    diferencia_escaner: int
    diferencia_fax: int
    
    # Período entre cierres
    dias_entre_cierres: int
    
    # Todos los usuarios con cambio (sin límite)
    top_usuarios_aumento: List[UsuarioComparacion]
    top_usuarios_disminucion: List[UsuarioComparacion]
    
    # Estadísticas
    total_usuarios_activos: int
    promedio_consumo_por_usuario: float



# ============================================================================
# Counter with Printer Info Schemas
# ============================================================================

class ContadorUsuarioWithPrinterResponse(BaseModel):
    """Response schema for user counter with printer info including capabilities"""
    # Counter data
    counter: ContadorUsuarioResponse
    
    # Printer info with capabilities
    printer: PrinterResponse
    
    class Config:
        from_attributes = True


class ReadCounterWithCapabilitiesResponse(BaseModel):
    """Response schema for read counter operation with printer capabilities"""
    success: bool
    printer_id: int
    contador_total: Optional[ContadorImpresoraResponse]
    usuarios_count: int
    error: Optional[str]
    
    # Printer info with capabilities
    printer: Optional[PrinterResponse]
