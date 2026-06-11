#!/usr/bin/env python3
"""
Diagnóstico: Verifica el flujo de datos B/N y Color en comparaciones de cierres.
Ejecutar desde: backend/
  python scripts/diagnostico_comparacion_bn_color.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import CierreMensual, CierreMensualUsuario, Printer
from services.close_service import CloseService

def fmt(n):
    return f"{n:>10,}"

def diagnosticar():
    db = SessionLocal()
    try:
        # ── 1. Listar todas las impresoras con cierres ──────────────────────
        printers_con_cierres = (
            db.query(Printer, CierreMensual)
            .join(CierreMensual, CierreMensual.printer_id == Printer.id)
            .distinct(Printer.id)
            .order_by(Printer.id)
            .all()
        )
        
        if not printers_con_cierres:
            print("❌ No hay impresoras con cierres en la BD.")
            return

        print("\n" + "="*80)
        print("  IMPRESORAS CON CIERRES DISPONIBLES")
        print("="*80)
        printer_ids_vistos = set()
        impresoras = []
        for p, c in printers_con_cierres:
            if p.id not in printer_ids_vistos:
                printer_ids_vistos.add(p.id)
                impresoras.append(p)
                n_cierres = db.query(CierreMensual).filter(CierreMensual.printer_id == p.id).count()
                print(f"  [{p.id:3d}] {p.hostname:<30s}  IP: {p.ip_address:<18s}  "
                      f"has_color={p.has_color}  cierres={n_cierres}")

        # ── 2. Para cada impresora, tomar los 2 cierres más recientes y comparar ──
        print("\n" + "="*80)
        print("  DIAGNÓSTICO DE DATOS B/N y COLOR POR IMPRESORA")
        print("="*80)

        for printer in impresoras:
            cierres = (
                db.query(CierreMensual)
                .filter(CierreMensual.printer_id == printer.id)
                .order_by(CierreMensual.fecha_fin.asc())
                .all()
            )
            if len(cierres) < 2:
                print(f"\n  ⚠️  [{printer.id}] {printer.hostname}: solo {len(cierres)} cierre — se necesitan ≥2.")
                continue

            c_antiguo = cierres[-2]
            c_reciente = cierres[-1]

            print(f"\n{'─'*80}")
            print(f"  Impresora: [{printer.id}] {printer.hostname}  |  has_color={printer.has_color}")
            print(f"  Cierre base:     [{c_antiguo.id}]  {c_antiguo.fecha_inicio} → {c_antiguo.fecha_fin}")
            print(f"  Cierre reciente: [{c_reciente.id}]  {c_reciente.fecha_inicio} → {c_reciente.fecha_fin}")

            # ── 2a. Verificar campos en CierreMensualUsuario ─────────────────
            usu_ant = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == c_antiguo.id
            ).limit(3).all()
            usu_rec = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == c_reciente.id
            ).limit(3).all()

            print(f"\n  📋 Muestra de usuarios en cierre BASE (primeros 3):")
            print(f"     {'user_id':>8}  {'total_pag':>10}  {'total_bn':>10}  {'total_color':>12}  "
                  f"{'cop_bn':>8}  {'cop_color':>10}  {'imp_bn':>8}  {'imp_color':>10}")
            for u in usu_ant:
                print(f"     {u.user_id:>8}  {fmt(u.total_paginas)}  {fmt(u.total_bn)}  {fmt(u.total_color)}  "
                      f"  {fmt(u.copiadora_bn)}  {fmt(u.copiadora_color)}  {fmt(u.impresora_bn)}  {fmt(u.impresora_color)}")

            print(f"\n  📋 Muestra de usuarios en cierre RECIENTE (primeros 3):")
            print(f"     {'user_id':>8}  {'total_pag':>10}  {'total_bn':>10}  {'total_color':>12}  "
                  f"{'cop_bn':>8}  {'cop_color':>10}  {'imp_bn':>8}  {'imp_color':>10}")
            for u in usu_rec:
                print(f"     {u.user_id:>8}  {fmt(u.total_paginas)}  {fmt(u.total_bn)}  {fmt(u.total_color)}  "
                      f"  {fmt(u.copiadora_bn)}  {fmt(u.copiadora_color)}  {fmt(u.impresora_bn)}  {fmt(u.impresora_color)}")

            # ── 2b. Ejecutar CloseService.comparar_cierres ───────────────────
            try:
                resultado = CloseService.comparar_cierres(db, c_antiguo.id, c_reciente.id)
                
                print(f"\n  ✅ RESULTADO comparar_cierres:")
                print(f"     diferencia_total   = {resultado['diferencia_total']:>12,}")
                print(f"     diferencia_bn      = {resultado.get('diferencia_bn', 'CAMPO FALTANTE'):>12}")
                print(f"     diferencia_color   = {resultado.get('diferencia_color', 'CAMPO FALTANTE'):>12}")
                print(f"     diferencia_cop     = {resultado['diferencia_copiadora']:>12,}")
                print(f"     diferencia_imp     = {resultado['diferencia_impresora']:>12,}")
                print(f"     diferencia_esc     = {resultado['diferencia_escaner']:>12,}")
                print(f"     total_usuarios     = {resultado['total_usuarios_activos']:>12,}")
                
                # Verificar usuarios en el resultado
                todos = resultado['top_usuarios_aumento'] + resultado['top_usuarios_disminucion']
                print(f"\n  👥 Muestra de usuarios en resultado API (primeros 3):")
                print(f"     {'nombre':<25}  {'c1_bn':>8}  {'c1_color':>9}  {'c2_bn':>8}  {'c2_color':>9}  "
                      f"{'dif_bn':>8}  NOTE")
                for u in todos[:3]:
                    bn1 = u.get('copiadora_bn_cierre1',0) + u.get('impresora_bn_cierre1',0)
                    bn2 = u.get('copiadora_bn_cierre2',0) + u.get('impresora_bn_cierre2',0)
                    col1 = u.get('copiadora_color_cierre1',0) + u.get('impresora_color_cierre1',0)
                    col2 = u.get('copiadora_color_cierre2',0) + u.get('impresora_color_cierre2',0)
                    note = "✅" if (col1 > 0 or col2 > 0) == printer.has_color else "⚠️ chk"
                    print(f"     {u['nombre_usuario']:<25}  {bn1:>8,}  {col1:>9,}  "
                          f"{bn2:>8,}  {col2:>9,}  {bn2-bn1:>+8,}  {note}")
                
                # Verificar consistencia has_color
                col_total = sum(
                    (u.get('copiadora_color_cierre2',0) + u.get('impresora_color_cierre2',0))
                    for u in todos
                )
                print(f"\n  🎨 Suma color total en todos los usuarios: {col_total:,}")
                if printer.has_color and col_total == 0:
                    print(f"     ⚠️  La impresora TIENE color pero todos los valores color son 0 — revisar datos en BD")
                elif not printer.has_color and col_total > 0:
                    print(f"     ⚠️  La impresora NO tiene color pero hay valores color > 0 — revisar has_color en BD")
                else:
                    print(f"     ✅ Consistente con has_color={printer.has_color}")

            except Exception as e:
                print(f"\n  ❌ Error al comparar: {e}")

        print("\n" + "="*80)
        print("  FIN DEL DIAGNÓSTICO")
        print("="*80 + "\n")

    finally:
        db.close()

if __name__ == "__main__":
    diagnosticar()
