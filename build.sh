#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- Executando o Script de Build ---"

# 1. Instala as dependências do Python a partir do requirements.txt
echo "Instalando pacotes Python..."
pip install -r requirements.txt

# 2. Instala os navegadores do Playwright
# A variável PLAYWRIGHT_BROWSERS_PATH=0 é a chave mágica.
# Ela força o Playwright a instalar os navegadores dentro da pasta do ambiente virtual,
# que o Render COM CERTEZA irá preservar para o ambiente de execução.
echo "Instalando o navegador Chromium do Playwright..."
PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium

echo "--- Script de Build Finalizado com Sucesso ---"