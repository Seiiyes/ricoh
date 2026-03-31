"""
Demo del AuditOrchestrator.

Ejecuta una auditoría de ejemplo en un proyecto temporal para demostrar
el funcionamiento completo del sistema.
"""

import tempfile
from pathlib import Path

from audit_system.orchestrator import AuditOrchestrator


def create_demo_project(tmpdir: str) -> None:
    """
    Crea un proyecto de demostración con varios problemas detectables.
    
    Args:
        tmpdir: Directorio temporal donde crear el proyecto
    """
    # Crear estructura backend
    backend_dir = Path(tmpdir) / "backend"
    backend_dir.mkdir()
    
    # Crear archivo con función larga (hallazgo de calidad)
    api_file = backend_dir / "api_users.py"
    api_file.write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users():
    # Función larga sin paginación
    users = []
    for i in range(150):
        user = db.query(User).filter(User.id == i).first()  # N+1 query
        users.append(user)
    return users

def process_data():
    # Función muy larga (>50 líneas)
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x = 27
    y = 28
    z = 29
    aa = 30
    bb = 31
    cc = 32
    dd = 33
    ee = 34
    ff = 35
    gg = 36
    hh = 37
    ii = 38
    jj = 39
    kk = 40
    ll = 41
    mm = 42
    nn = 43
    oo = 44
    pp = 45
    qq = 46
    rr = 47
    ss = 48
    tt = 49
    uu = 50
    vv = 51
    return vv
""")
    
    # Crear archivo con secret hardcodeado (hallazgo de seguridad)
    config_file = backend_dir / "config.py"
    config_file.write_text("""
import os

# Secret hardcodeado - CRÍTICO
SECRET_KEY = "my-super-secret-key-12345"
API_KEY = "sk-1234567890abcdef"

# Configuración insegura
DEBUG = True
""")
    
    # Crear requirements.txt
    requirements = backend_dir / "requirements.txt"
    requirements.write_text("""fastapi==0.95.0
sqlalchemy==1.4.0
pydantic==1.10.0
""")
    
    # Crear estructura frontend
    src_dir = Path(tmpdir) / "src"
    src_dir.mkdir()
    
    # Crear componente grande sin tests (hallazgo de testing)
    component_file = src_dir / "UserList.tsx"
    component_code = """
import React, { useState, useEffect } from 'react';

export function UserList() {
    const [users, setUsers] = useState([]);
    
    // useEffect sin array de dependencias
    useEffect(() => {
        fetch('/api/users')
            .then(res => res.json())
            .then(data => setUsers(data));
    });
    
    return (
        <div>
"""
    # Agregar muchas líneas para hacer el componente grande
    for i in range(200):
        component_code += f"            <div>Line {i}</div>\n"
    
    component_code += """        </div>
    );
}
"""
    component_file.write_text(component_code)
    
    # Crear package.json
    package_json = Path(tmpdir) / "package.json"
    package_json.write_text("""{
    "dependencies": {
        "react": "^18.0.0",
        "axios": "^0.27.0"
    },
    "devDependencies": {
        "typescript": "^4.9.0"
    }
}""")


def main():
    """Ejecuta demo del AuditOrchestrator."""
    print("=== Demo del AuditOrchestrator ===\n")
    
    # Crear proyecto temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Creando proyecto de demostración en: {tmpdir}\n")
        create_demo_project(tmpdir)
        
        # Inicializar orchestrator
        print("Inicializando AuditOrchestrator...")
        orchestrator = AuditOrchestrator()
        print("✓ Orchestrator inicializado\n")
        
        # Ejecutar auditoría
        print("Ejecutando auditoría completa...\n")
        report, output_path = orchestrator.run_audit(tmpdir)
        
        # Mostrar resumen del reporte
        print("\n=== REPORTE GENERADO ===\n")
        print(f"Reporte guardado en: {output_path}")
        print(f"Longitud del reporte: {len(report)} caracteres")
        print(f"Líneas del reporte: {len(report.splitlines())}")
        
        # Mostrar primeras líneas del reporte
        print("\n--- Primeras 50 líneas del reporte ---\n")
        lines = report.splitlines()
        for line in lines[:50]:
            print(line)
        
        print("\n--- Fin del demo ---")


if __name__ == "__main__":
    main()
