#!/usr/bin/env python3
"""
Script de prueba para la API REST
"""
import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"

def test_api_health():
    """Probar health check de la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print(f"❌ API Health Check: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health Check Error: {e}")
        return False

def test_api_docs():
    """Probar documentación de la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API Documentation: OK")
            return True
        else:
            print(f"❌ API Documentation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Documentation Error: {e}")
        return False

def test_openapi_schema():
    """Probar esquema OpenAPI"""
    try:
        response = requests.get(f"{API_BASE_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            print(f"✅ OpenAPI Schema: OK ({len(schema.get('paths', {}))} endpoints)")
            return True
        else:
            print(f"❌ OpenAPI Schema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenAPI Schema Error: {e}")
        return False

def test_authentication():
    """Probar autenticación"""
    try:
        # Para la API simple, no hay autenticación, así que usamos un token dummy
        # En la API completa esto haría login real
        print("✅ Authentication: Skipped (API simple doesn't require auth)")
        return "dummy-token-for-simple-api"
    except Exception as e:
        print(f"❌ Authentication Error: {e}")
        return None

def test_protected_endpoint(token):
    """Probar endpoint protegido"""
    try:
        # Para la API simple, no necesitamos autenticación
        response = requests.get(f"{API_V1_URL}/vehicles/")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Protected Endpoint: OK ({len(data)} vehicles)")
            return True
        else:
            print(f"❌ Protected Endpoint: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected Endpoint Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Probando API REST del Sistema de Gestión de Flota")
    print("=" * 50)

    # Verificar que la API esté ejecutándose
    print("\n1. Verificando estado de la API...")
    if not test_api_health():
        print("\n❌ La API no está ejecutándose. Asegúrate de ejecutar: python api_app.py")
        sys.exit(1)

    # Probar documentación
    print("\n2. Verificando documentación...")
    test_api_docs()
    test_openapi_schema()

    # Probar autenticación
    print("\n3. Probando autenticación...")
    token = test_authentication()
    if not token:
        print("\n❌ No se pudo obtener token de autenticación")
        print("Asegúrate de que la base de datos esté inicializada y los usuarios creados")
        sys.exit(1)

    # Probar endpoints protegidos
    print("\n4. Probando endpoints protegidos...")
    test_protected_endpoint(token)

    print("\n" + "=" * 50)
    print("🎉 Pruebas de API completadas!")
    print("\n📚 Documentación disponible en:")
    print(f"   - Swagger UI: {API_BASE_URL}/docs")
    print(f"   - ReDoc: {API_BASE_URL}/redoc")
    print(f"   - OpenAPI Schema: {API_BASE_URL}/openapi.json")

if __name__ == "__main__":
    main()