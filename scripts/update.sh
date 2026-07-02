#!/bin/bash
set -e
echo "========================================="
echo "📥 Descargando actualizaciones de Git..."
echo "========================================="
# git pull (desactivado para no sobreescribir cambios manuales)

echo "⚙️  Configurando docker-compose..."
cp deployment/docker-compose.server131.yml docker-compose.yml

echo "🐳 Reconstruyendo e iniciando contenedores..."
docker compose up --build -d

echo "========================================="
echo "✅ ACTUALIZACIÓN COMPLETADA CON ÉXITO"
echo "========================================="
