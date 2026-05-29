import sys
errors = []

# Test 1: Imports completos de counters.py
try:
    from db.models import User, CierreMensual, CierreMensualUsuario, Printer, ContadorImpresora, ContadorUsuario, ComparacionGuardada
    from sqlalchemy import or_
    from api.counter_schemas import ContadorImpresoraResponse, ContadorUsuarioResponse, CierreMensualResponse, ComparacionGuardadaCreate, ComparacionGuardadaResponse
    from services.counter_service import CounterService
    from services.close_service import CloseService
    from middleware.auth_middleware import get_current_user
    from services.company_filter_service import CompanyFilterService
    print('[OK] counters.py imports')
except Exception as e:
    errors.append(f'[FAIL] counters imports: {e}')

# Test 2: Imports de dashboard.py (Printer incluido)
try:
    from db.models import Printer
    from api import dashboard
    print('[OK] dashboard.py imports (Printer presente)')
except Exception as e:
    errors.append(f'[FAIL] dashboard imports: {e}')

# Test 3: export.py sin csv
try:
    from openpyxl import Workbook
    from api import export
    if hasattr(export, 'csv'):
        errors.append('[FAIL] export.py aun tiene referencia csv')
    else:
        print('[OK] export.py sin modulo csv')
except Exception as e:
    errors.append(f'[FAIL] export imports: {e}')

# Test 4: AdminUser.nombre_completo existe (es el current_user real del middleware)
try:
    from db.models import AdminUser
    from db.database import SessionLocal
    db = SessionLocal()
    admin = db.query(AdminUser).first()
    if admin:
        _ = admin.nombre_completo
        print(f'[OK] AdminUser.nombre_completo existe: "{str(admin.nombre_completo)[:30]}"')
    else:
        # Verificar que el campo existe aunque no haya registros
        cols = [c.name for c in AdminUser.__table__.columns]
        if 'nombre_completo' in cols:
            print('[OK] AdminUser.nombre_completo existe (tabla vacia)')
        else:
            errors.append('[FAIL] AdminUser no tiene campo nombre_completo')
    db.close()
except Exception as e:
    errors.append(f'[FAIL] AdminUser.nombre_completo: {e}')

# Test 5: AdminUser.empresa_id existe (para el fallback de empresa_id)
try:
    from db.models import AdminUser
    cols = [c.name for c in AdminUser.__table__.columns]
    if 'empresa_id' in cols:
        print('[OK] AdminUser.empresa_id existe (fallback empresa_id)')
    else:
        errors.append('[FAIL] AdminUser sin empresa_id - fallback roto')
except Exception as e:
    errors.append(f'[FAIL] AdminUser.empresa_id check: {e}')

# Test 6: ComparacionGuardada.empresa_id NOT NULL
try:
    from db.models import ComparacionGuardada
    cols = [c.name for c in ComparacionGuardada.__table__.columns]
    if 'empresa_id' in cols:
        print('[OK] ComparacionGuardada.empresa_id existe')
    else:
        errors.append('[FAIL] ComparacionGuardada sin empresa_id')
except Exception as e:
    errors.append(f'[FAIL] ComparacionGuardada check: {e}')

# Test 7: User.name existe (campo correcto en el modelo User de impresoras)
try:
    from db.models import User
    cols = [c.name for c in User.__table__.columns]
    if 'name' in cols:
        print('[OK] User.name existe (campo correcto en modelo User de impresoras)')
    else:
        errors.append('[FAIL] User sin campo name')
except Exception as e:
    errors.append(f'[FAIL] User.name check: {e}')

# Test 8: Verificar que export.py tiene los endpoints Excel
try:
    from api.export import export_cierre_excel, export_comparacion_excel, export_comparacion_excel_ricoh
    print('[OK] Endpoints Excel en export.py presentes')
except Exception as e:
    errors.append(f'[FAIL] Endpoints Excel en export.py: {e}')

# Test 9: Verificar que los endpoints CSV NO existen en export.py
try:
    from api.export import export_cierre
    errors.append('[FAIL] export_cierre (CSV) TODAVIA existe - no fue eliminado')
except ImportError:
    print('[OK] export_cierre (CSV) eliminado correctamente')

try:
    from api.export import export_comparacion
    errors.append('[FAIL] export_comparacion (CSV) TODAVIA existe - no fue eliminado')
except ImportError:
    print('[OK] export_comparacion (CSV) eliminado correctamente')

# Resultado final
print()
if errors:
    print('=== ERRORES ENCONTRADOS ===')
    for err in errors:
        print(err)
    sys.exit(1)
else:
    print('=== TODOS LOS CHECKS PASARON - LISTO PARA COMMIT ===')
