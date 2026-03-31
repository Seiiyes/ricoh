"""
Demo del CLI del sistema de auditoría.

Muestra ejemplos de uso del CLI sin ejecutar auditorías reales.
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_section(title: str):
    """Imprime un título de sección."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def main():
    """Muestra ejemplos de uso del CLI."""
    print_section("Demo del CLI - Sistema de Auditoría")
    
    print("El CLI proporciona una interfaz de línea de comandos para ejecutar")
    print("auditorías de código con opciones configurables.\n")
    
    print_section("Uso Básico")
    print("Auditar proyecto actual:")
    print("  python audit_system/cli.py -p .\n")
    
    print("Auditar proyecto específico:")
    print("  python audit_system/cli.py -p /path/to/project\n")
    
    print_section("Opciones Disponibles")
    
    print("1. --project-path, -p (REQUERIDO)")
    print("   Ruta del proyecto a auditar")
    print("   Ejemplo: -p . o --project-path /path/to/project\n")
    
    print("2. --output, -o (OPCIONAL)")
    print("   Ruta del archivo de reporte")
    print("   Default: docs/OPTIMIZACION_HALLAZGOS.md")
    print("   Ejemplo: -o custom/report.md\n")
    
    print("3. --verbose, -v (FLAG)")
    print("   Habilita logging detallado")
    print("   Ejemplo: -v o --verbose\n")
    
    print("4. --categories, -c (OPCIONAL)")
    print("   Filtrar categorías de análisis (funcionalidad futura)")
    print("   Ejemplo: -c performance,security\n")
    
    print_section("Ejemplos de Uso")
    
    print("1. Auditoría básica del proyecto actual:")
    print("   python audit_system/cli.py -p .\n")
    
    print("2. Auditoría con reporte personalizado:")
    print("   python audit_system/cli.py -p . -o reports/audit_2024.md\n")
    
    print("3. Auditoría con logging detallado:")
    print("   python audit_system/cli.py -p . --verbose\n")
    
    print("4. Auditoría con categorías específicas:")
    print("   python audit_system/cli.py -p . -c performance,security\n")
    
    print("5. Auditoría completa con todas las opciones:")
    print("   python audit_system/cli.py -p . -o custom.md -v -c all\n")
    
    print_section("Script de Ejecución Simple")
    
    print("Para ejecutar una auditoría rápida del proyecto Ricoh Suite:")
    print("  python run_audit.py\n")
    
    print("Este script:")
    print("  - Analiza backend/ y frontend/src/")
    print("  - Genera reporte en docs/OPTIMIZACION_HALLAZGOS.md")
    print("  - Muestra progreso en consola\n")
    
    print_section("Ayuda")
    
    print("Para ver todas las opciones disponibles:")
    print("  python audit_system/cli.py --help\n")
    
    print("=" * 60)
    print("  Demo completado")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
