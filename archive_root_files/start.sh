#!/bin/bash
# Script de inicio simplificado para Gestión de Flota
# Compatible con Windows, Linux y macOS

echo "🚀 Iniciando Sistema de Gestión de Flota - Junta de Andalucía"
echo "================================================================"

# Función para detectar el sistema operativo
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "Linux" ;;
        Darwin*)    echo "macOS" ;;
        CYGWIN*|MINGW*|MSYS*) echo "Windows" ;;
        *)          echo "Unknown" ;;
    esac
}

OS=$(detect_os)
echo "📱 Sistema operativo detectado: $OS"

# Función para activar entorno virtual
activate_venv() {
    if [ "$OS" = "Windows" ]; then
        if [ -d "venv" ]; then
            echo "🔧 Activando entorno virtual..."
            source venv/Scripts/activate
        else
            echo "❌ No se encontró el entorno virtual. Ejecuta: python -m venv venv"
            exit 1
        fi
    else
        if [ -d "venv" ]; then
            echo "🔧 Activando entorno virtual..."
            source venv/bin/activate
        else
            echo "❌ No se encontró el entorno virtual. Ejecuta: python -m venv venv"
            exit 1
        fi
    fi
}

# Función para verificar dependencias
check_dependencies() {
    echo "🔍 Verificando dependencias..."

    # Verificar Python
    if ! command -v python &> /dev/null; then
        echo "❌ Python no está instalado"
        exit 1
    fi

    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "✅ Python $PYTHON_VERSION encontrado"

    # Verificar si requirements.txt existe
    if [ ! -f "requirements.txt" ]; then
        echo "❌ No se encontró requirements.txt"
        exit 1
    fi

    # Instalar dependencias si no están instaladas
    if ! python -c "import flask, sqlalchemy" &> /dev/null; then
        echo "📦 Instalando dependencias..."
        pip install -r requirements.txt
    else
        echo "✅ Dependencias ya instaladas"
    fi
}

# Función para iniciar la aplicación
start_app() {
    echo "🚀 Iniciando aplicación..."

    # Crear archivo .env si no existe
    if [ ! -f ".env" ]; then
        echo "📋 Creando archivo .env..."
        cp .env.example .env
    fi

    # Iniciar la aplicación
    echo "🌐 Iniciando servidor en http://127.0.0.1:5000"
    echo "📖 Consulta QUICK_START.md para más información"
    echo ""
    echo "💡 Credenciales iniciales:"
    echo "   Usuario: admin"
    echo "   Contraseña: admin123"
    echo ""
    echo "⏹️  Presiona Ctrl+C para detener el servidor"
    echo ""

    python run.py
}

# Ejecutar funciones
activate_venv
check_dependencies
start_app
