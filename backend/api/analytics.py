from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db
from services.redis_service import cache_result
from datetime import date
from typing import Optional
from middleware.auth_middleware import get_current_user
import os

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/evolution")
@cache_result("analytics:evolution", ttl=3600)
async def get_evolution(
    meses: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """
    Get consumption evolution
    Cached for 1 hour
    """
    result = db.execute(
        text("SELECT * FROM get_evolucion_consumo(:meses)"),
        {"meses": meses}
    ).fetchall()
    
    return [
        {
            "name": row.mes_nombre,
            "paginas": row.total_paginas,
            "anio": row.anio,
            "mes": row.mes
        }
        for row in result
    ]

@router.get("/comparison")
@cache_result("analytics:comparison", ttl=3600)
async def get_comparison(
    fecha_inicio_a: date = Query(...),
    fecha_fin_a: date = Query(...),
    fecha_inicio_b: date = Query(...),
    fecha_fin_b: date = Query(...),
    db: Session = Depends(get_db)
):
    """
    Compare two periods
    Cached for 1 hour
    """
    result = db.execute(
        text("SELECT * FROM get_comparativa_periodos(:ia, :fa, :ib, :fb)"),
        {
            "ia": fecha_inicio_a,
            "fa": fecha_fin_a,
            "ib": fecha_inicio_b,
            "fb": fecha_fin_b
        }
    ).fetchall()
    
    return [
        {
            "indicador": row.indicador,
            "periodoA": row.periodo_a,
            "periodoB": row.periodo_b,
            "variacion": float(row.variacion)
        }
        for row in result
    ]


@router.get("/top-users")
async def get_top_users(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    limit: int = Query(10, ge=1, le=100),
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtiene el ranking de usuarios con mayor consumo en un rango de fechas.
    Implementa multi-tenancy estricto para filtrar por empresa.
    """
    # Determinar la empresa a la que se debe filtrar
    target_empresa_id = empresa_id
    if not current_user.is_superadmin():
        target_empresa_id = current_user.empresa_id
    
    # Consulta robusta con desglose completo por función y multi-tenancy
    query = """
        SELECT
            u.id as user_id,
            u.name as nombre,
            u.codigo_de_usuario as codigo_usuario,
            cc.nombre as centro_costos,
            SUM(cmu.consumo_total)::BIGINT AS total_consumo_paginas,
            SUM(cmu.consumo_copiadora)::BIGINT AS total_copiadora,
            SUM(cmu.consumo_impresora)::BIGINT AS total_impresora,
            SUM(cmu.consumo_escaner)::BIGINT AS total_escaner,
            SUM(cmu.consumo_fax)::BIGINT AS total_fax,
            COUNT(*)::INTEGER AS cierres_count
        FROM cierres_mensuales_usuarios cmu
        INNER JOIN cierres_mensuales cm ON cm.id = cmu.cierre_mensual_id
        INNER JOIN printers p ON p.id = cm.printer_id
        INNER JOIN users u ON u.id = cmu.user_id
        LEFT JOIN centro_costos cc ON u.centro_costo_id = cc.id
        WHERE cm.fecha_inicio >= :inicio
          AND cm.fecha_fin <= :fin
    """
    
    params = {"inicio": fecha_inicio, "fin": fecha_fin, "limit": limit}
    
    if target_empresa_id is not None:
        query += " AND p.empresa_id = :empresa_id"
        params["empresa_id"] = target_empresa_id
        
    query += """
        GROUP BY u.id, u.name, u.codigo_de_usuario, cc.nombre
        ORDER BY total_consumo_paginas DESC NULLS LAST
        LIMIT :limit
    """
    
    result = db.execute(text(query), params).fetchall()
    
    return [
        {
            "user_id": row.user_id,
            "nombre": row.nombre,
            "codigo_usuario": row.codigo_usuario,
            "centro_costos": row.centro_costos,
            "total_consumo_paginas": int(row.total_consumo_paginas or 0),
            "total_copiadora": int(row.total_copiadora or 0),
            "total_impresora": int(row.total_impresora or 0),
            "total_escaner": int(row.total_escaner or 0),
            "total_fax": int(row.total_fax or 0),
            "cierres_count": row.cierres_count,
        }
        for row in result
    ]

