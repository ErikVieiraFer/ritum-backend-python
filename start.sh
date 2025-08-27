set -e

echo "--- Iniciando script start.sh ---"

echo "Instalando navegadores do Playwright..."
playwright install chromium

echo "Iniciando o servidor Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port $PORT