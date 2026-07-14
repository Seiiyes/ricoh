#  Guía de Configuración del Entorno de Desarrollo (Setup)

Esta guía detalla los requisitos, pasos de instalación, configuración de variables de entorno y estándares de formateo de código exigidos para el equipo de desarrollo de **Ricoh Equipment Manager**.

---

## ️ 1. Requisitos Previos

Asegúrate de tener instaladas las siguientes herramientas en tu máquina local:
*   **Docker Desktop**: Versión 24.0 o superior (con soporte para Compose V2).
*   **Node.js**: Versión 20.x (LTS) o superior.
*   **Python**: Versión 3.11+ (con soporte para entornos virtuales `venv` y gestor `pip`).
*   **Git**: Para control de versiones.

---

##  2. Configuración del Entorno Local

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd ricoh
```

### 2. Configuración del Frontend
Instala las dependencias y prepara el entorno local:
```bash
npm install
```

### 3. Configuración del Backend
Se recomienda crear un entorno virtual para que las herramientas de autocompletado y linters de tu editor local funcionen correctamente:
```bash
cd backend
python -m venv venv

# En Windows:
.\venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

---

##  3. Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto y en el directorio `backend/`. 

### Archivo `.env` en Backend (`backend/.env`)
```env
# Configuración del entorno
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# Base de datos
DATABASE_URL=postgresql://ricoh_admin:Admin123!@localhost:5432/ricoh_fleet

# Seguridad (generar valores robustos en producción)
SECRET_KEY=dev_secret_key_change_me_in_production
ENCRYPTION_KEY=dev_encryption_key_change_me_in_prod_aes256_key==

# Redis
REDIS_URL=redis://localhost:6379/0

# Ricoh Integración
RICOH_ADMIN_PASSWORD=Admin123!
```

---

##  4. Estándar de Formateo y Estilo de Código

Para garantizar que el código se mantenga limpio y uniforme, el equipo de desarrollo debe adherirse a los formateadores automáticos.

### ️ Frontend (React & TypeScript)
*   **Formateador**: **Prettier** v3+
*   **Linter**: **ESLint** v9+ (incluido en las dependencias y ejecutado al compilar).
*   **Reglas Clave**:
    *   Uso de comillas simples (`'`) para strings en TS/TSX.
    *   Punto y coma obligatorio (`semi: true`).
    *   Tabulación de 2 espacios.

###  Backend (Python & FastAPI)
*   **Formateador**: **Black** o **PEP 8**.
*   **Linter**: **Flake8** / **Pylint**.
*   **Reglas Clave**:
    *   Longitud máxima de línea: 88 o 120 caracteres.
    *   Tabulación de 4 espacios.

---

##  5. Extensiones Obligatorias para VS Code

Si utilizas Visual Studio Code, debes instalar las siguientes extensiones:

1.  **Prettier - Code Formatter** (`esbenp.prettier-vscode`): Habilita el formateo al guardar.
2.  **ESLint** (`dbaeumer.vscode-eslint`): Resalta errores sintácticos y de estilo en tiempo real en el frontend.
3.  **Python** (`ms-python.python`): Soporte de autocompletado y análisis estático.
4.  **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`): Autocompletado de clases CSS Tailwind.
5.  **Pylance** (`ms-python.vscode-pylance`): Motor de análisis de lenguaje avanzado para Python.

### Configuración sugerida de VS Code (`.vscode/settings.json`)
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```
