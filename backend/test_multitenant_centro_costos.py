"""
Script de verificación: Prueba de Centros de Costo Multitenant
Ejecutar: docker exec ricoh-backend python /app/test_multitenant_centro_costos.py
"""
import sys
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User, CentroCosto, SMBServer, NetworkCredential
from db.models_auth import Empresa
from db.repository import UserRepository

def run_test():
    print("=" * 60)
    print("  INICIANDO PRUEBA DE CENTROS DE COSTOS MULTITENANT")
    print("=" * 60)
    
    db: Session = SessionLocal()
    
    empresa_a = None
    empresa_b = None
    user_a = None
    user_b = None
    cc_a = None
    cc_b = None
    
    try:
        # 1. Crear Empresas de prueba
        print("\n1. Creando empresas de prueba...")
        empresa_a = Empresa(
            razon_social="Empresa A SAS de Prueba",
            nombre_comercial="Empresa A",
            nit="900.111.222-1",
            is_active=True
        )
        empresa_b = Empresa(
            razon_social="Empresa B SAS de Prueba",
            nombre_comercial="Empresa B",
            nit="900.333.444-2",
            is_active=True
        )
        db.add(empresa_a)
        db.add(empresa_b)
        db.flush()
        print(f"   ✓ Empresa A creada con ID={empresa_a.id}")
        print(f"   ✓ Empresa B creada con ID={empresa_b.id}")
        
        # 2. Crear Centros de costo con mismo nombre para ambas empresas
        print("\n2. Creando centros de costo 'Contabilidad'...")
        cc_a = CentroCosto(
            nombre="Contabilidad",
            empresa_id=empresa_a.id
        )
        cc_b = CentroCosto(
            nombre="Contabilidad",
            empresa_id=empresa_b.id
        )
        db.add(cc_a)
        db.add(cc_b)
        db.flush()
        print(f"   ✓ Centro costo A 'Contabilidad' creado con ID={cc_a.id} (empresa_id={cc_a.empresa_id})")
        print(f"   ✓ Centro costo B 'Contabilidad' creado con ID={cc_b.id} (empresa_id={cc_b.empresa_id})")
        
        # Validación de unicidad de IDs
        assert cc_a.id != cc_b.id, "ERROR: Los centros de costo tienen el mismo ID"
        print("   ✓ OK: Los centros de costo tienen IDs diferentes e independientes en la base de datos!")
        
        # 3. Crear Usuarios asociados a las respectivas empresas y centros
        print("\n3. Creando usuarios de prueba mediante el Repositorio...")
        
        # Requerimos SMB y Credenciales por defecto para el repositorio
        smb = db.query(SMBServer).first()
        if not smb:
            smb = SMBServer(server_address="192.168.91.5", port=21, description="Default")
            db.add(smb)
            db.flush()
            
        cred = db.query(NetworkCredential).first()
        if not cred:
            cred = NetworkCredential(username="reliteltda\\scaner", password_encrypted="123", description="Default")
            db.add(cred)
            db.flush()
            
        user_a = UserRepository.create(
            db=db,
            name="Usuario Empresa A",
            codigo_de_usuario="9991",
            network_username=cred.username,
            network_password_encrypted=cred.password_encrypted,
            smb_server=smb.server_address,
            smb_port=smb.port,
            smb_path="\\\\server\\scan_a",
            empresa=empresa_a.razon_social,
            centro_costos="Contabilidad"
        )
        
        user_b = UserRepository.create(
            db=db,
            name="Usuario Empresa B",
            codigo_de_usuario="9992",
            network_username=cred.username,
            network_password_encrypted=cred.password_encrypted,
            smb_server=smb.server_address,
            smb_port=smb.port,
            smb_path="\\\\server\\scan_b",
            empresa=empresa_b.razon_social,
            centro_costos="Contabilidad"
        )
        
        print(f"   ✓ Usuario A creado: {user_a.name} (empresa_id={user_a.empresa_id}, centro_costo_id={user_a.centro_costo_id})")
        print(f"   ✓ Usuario B creado: {user_b.name} (empresa_id={user_b.empresa_id}, centro_costo_id={user_b.centro_costo_id})")
        
        # 4. Validaciones de la regla de negocio
        print("\n4. Ejecutando aserciones de reglas de negocio...")
        
        # Verificar que apuntan a IDs de centros de costo diferentes
        assert user_a.centro_costo_id == cc_a.id, f"ERROR: Usuario A no apunta a Centro A. Tiene {user_a.centro_costo_id}"
        assert user_b.centro_costo_id == cc_b.id, f"ERROR: Usuario B no apunta a Centro B. Tiene {user_b.centro_costo_id}"
        print("   ✓ OK: Cada usuario está asociado al centro de costo correspondiente a su propia empresa!")
        
        # Verificar la propiedad compatible retrocompatible centro_costos
        assert user_a.centro_costos == "Contabilidad", f"ERROR: Propiedad centro_costos en A devolvió {user_a.centro_costos}"
        assert user_b.centro_costos == "Contabilidad", f"ERROR: Propiedad centro_costos en B devolvió {user_b.centro_costos}"
        print("   ✓ OK: Ambos usuarios devuelven 'Contabilidad' a través de la propiedad dinámica string!")
        
        print("\n🎉 ¡TODAS LAS PRUEBAS DE MIGRACIÓN MULTITENANT PASARON CON ÉXITO ROTUNDO!")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 5. Limpieza de base de datos
        print("\n5. Limpiando datos de prueba...")
        if user_a:
            db.delete(user_a)
        if user_b:
            db.delete(user_b)
        if cc_a:
            db.delete(cc_a)
        if cc_b:
            db.delete(cc_b)
        if empresa_a:
            db.delete(empresa_a)
        if empresa_b:
            db.delete(empresa_b)
            
        db.commit()
        db.close()
        print("   ✓ Base de datos limpia y restaurada.")
        print("-" * 60)

if __name__ == "__main__":
    run_test()
