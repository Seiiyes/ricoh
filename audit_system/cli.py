"""
CLI para el sistema de auditoría de código.

Proporciona interfaz de línea de comandos para ejecutar auditorías
con opciones configurables.
"""

import argparse
import sys
from pathlib import Path

from audit_system.orchestrator import AuditOrchestrator
from audit_system.logger import get_logger
from audit_system.config import get_config, update_config

logger = get_logger(__name__)


def parse_arguments():
    """
    Parsea argumentos de línea de comandos.
    
    Returns:
        Namespace con argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Sistema de auditoría y optimización de código",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -p . -o docs/reporte.md
  %(prog)s --project-path /path/to/project --verbose
  %(prog)s -p . -c performance,security
        """
    )
    
    parser.add_argument(
        "-p", "--project-path",
        type=str,
        required=True,
        help="Ruta del proyecto a auditar"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Ruta del archivo de reporte (default: docs/OPTIMIZACION_HALLAZGOS.md)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Habilitar logging detallado"
    )
    
    parser.add_argument(
        "-c", "--categories",
        type=str,
        default=None,
        help="Filtrar categorías de análisis (separadas por comas, ej: performance,security)"
    )
    
    return parser.parse_args()


def main():
    """Función principal del CLI."""
    try:
        # Parsear argumentos
        args = parse_arguments()
        
        # Configurar logging
        if args.verbose:
            update_config(LOG_LEVEL="DEBUG")
            logger.setLevel("DEBUG")
            logger.info("Modo verbose activado")
        
        # Validar ruta del proyecto
        project_path = Path(args.project_path)
        if not project_path.exists():
            logger.error(f"La ruta del proyecto no existe: {args.project_path}")
            sys.exit(1)
        
        if not project_path.is_dir():
            logger.error(f"La ruta del proyecto no es un directorio: {args.project_path}")
            sys.exit(1)
        
        # Log de categorías (funcionalidad futura)
        if args.categories:
            logger.info(f"Categorías especificadas: {args.categories}")
            logger.warning("El filtrado por categorías aún no está implementado")
        
        # Inicializar orquestador
        logger.info("Inicializando sistema de auditoría...")
        orchestrator = AuditOrchestrator()
        
        # Ejecutar auditoría
        logger.info(f"Ejecutando auditoría del proyecto: {args.project_path}")
        report, output_path = orchestrator.run_audit(
            project_path=str(project_path.resolve()),
            output_path=args.output
        )
        
        # Resultado exitoso
        print(f"\n✓ Auditoría completada exitosamente")
        print(f"✓ Reporte generado en: {output_path}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Auditoría interrumpida por el usuario")
        print("\n✗ Auditoría cancelada")
        return 130
        
    except Exception as e:
        logger.error(f"Error durante la auditoría: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
