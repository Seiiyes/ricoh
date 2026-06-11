import os
import sys

def load_ssh_config():
    """
    Loads SSH configuration from environment variables or a local .env file.
    Searches multiple potential paths to ensure it works regardless of the cwd.
    """
    host = os.getenv("REMOTE_SSH_HOST", "192.168.91.131")
    user = os.getenv("REMOTE_SSH_USER", "odootic")
    password = os.getenv("REMOTE_SSH_PASS")
    
    if not password:
        # List of potential paths to search for .env
        paths_to_check = [
            ".env",
            "../.env",
            "../../.env",
            os.path.join(os.path.dirname(__file__), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        ]
        for path in paths_to_check:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                k, v = line.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip('"').strip("'")
                                if k == "REMOTE_SSH_HOST":
                                    host = v
                                elif k == "REMOTE_SSH_USER":
                                    user = v
                                elif k == "REMOTE_SSH_PASS":
                                    password = v
                except Exception:
                    pass
                if password:
                    break
                    
    if not password:
        print("\n" + "="*80)
        print("❌ ERROR DE SEGURIDAD: La contraseña SSH no está configurada.")
        print("="*80)
        print("  Para ejecutar este script, debes definir la contraseña en un archivo '.env'.")
        print("  Crea un archivo '.env' en la raíz del proyecto y agrega:")
        print("     REMOTE_SSH_PASS=TuContraseñaSsh")
        print("="*80 + "\n")
        sys.exit(1)
        
    return host, user, password
