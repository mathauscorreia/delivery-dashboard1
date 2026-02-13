#!/bin/bash

# Script de inicialização do Delivery Optimizer
# Verifica dependências e inicia o servidor

echo "============================================================"
echo "🚚 DELIVERY OPTIMIZER - Inicialização"
echo "============================================================"
echo ""

# Verifica se Python está instalado
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 não encontrado!"
    echo "   Por favor, instale Python 3.11 ou superior"
    exit 1
fi

echo "✅ Python $(python3.11 --version) encontrado"

# Verifica se as dependências estão instaladas
echo "🔍 Verificando dependências..."

if ! python3.11 -c "import flask" &> /dev/null; then
    echo "⚠️  Dependências não instaladas. Instalando..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar dependências"
        exit 1
    fi
    
    echo "✅ Dependências instaladas com sucesso"
else
    echo "✅ Dependências já instaladas"
fi

# Cria diretórios necessários
mkdir -p uploads output

echo ""
echo "🚀 Iniciando servidor..."
echo ""

# Inicia o servidor Flask
python3.11 app.py
