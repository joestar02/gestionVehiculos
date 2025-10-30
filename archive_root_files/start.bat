@echo off
echo 🚀 Iniciando Sistema de Gestión de Flota - Junta de Andalucía
echo ================================================================
echo.

REM Activar entorno virtual
if exist .venv\Scripts\activate.bat (
    echo 🔧 Activando entorno virtual (.venv)...
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo 🔧 Activando entorno virtual (venv)...
    call venv\Scripts\activate.bat
) else (
    echo ❌ No se encontró el entorno virtual
    echo Ejecuta: python -m venv venv
    pause
    exit /b 1
)

REM Verificar dependencias
echo 🔍 Verificando dependencias...
python -c "import flask, sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo ✅ Dependencias ya instaladas
)

REM Crear .env si no existe
if not exist ".env" (
    echo 📋 Creando archivo .env...
    copy .env.example .env >nul
)

echo.
echo 🌐 Iniciando servidor en http://127.0.0.1:5000
echo 📖 Consulta QUICK_START.md para más información
echo.
echo 💡 Credenciales iniciales:
echo    Usuario: admin
echo    Contraseña: admin123
echo.
echo ⏹️  Presiona Ctrl+C para detener el servidor
echo.

python run.py

pause
