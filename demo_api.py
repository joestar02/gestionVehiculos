#!/usr/bin/env python3
"""
Demo script - Ejemplo de uso de la API REST
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def demo_vehicles():
    """Demo: Operaciones con vehículos"""
    print_section("🚗 DEMO: Gestión de Vehículos")
    
    # Listar vehículos
    print("1️⃣ Listando vehículos existentes...")
    response = requests.get(f"{API_V1}/vehicles/")
    vehicles = response.json()
    for v in vehicles:
        print(f"   - {v['license_plate']}: {v['make']} {v['model']} ({v['year']})")
    
    # Crear nuevo vehículo
    print("\n2️⃣ Creando nuevo vehículo...")
    new_vehicle = {
        "license_plate": "MAL-9999",
        "make": "Volkswagen",
        "model": "Transporter",
        "year": 2023
    }
    response = requests.post(f"{API_V1}/vehicles", json=new_vehicle)
    if response.status_code == 200:
        vehicle = response.json()
        print(f"   ✅ Vehículo creado con ID: {vehicle['id']}")
        print(f"      - Matrícula: {vehicle['license_plate']}")
        print(f"      - Modelo: {vehicle['make']} {vehicle['model']}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # Obtener vehículo específico
    print("\n3️⃣ Obteniendo detalles de vehículo (ID: 1)...")
    response = requests.get(f"{API_V1}/vehicles/1")
    if response.status_code == 200:
        vehicle = response.json()
        print(f"   ✅ Vehículo encontrado:")
        print(json.dumps(vehicle, indent=4, default=str))
    else:
        print(f"   ❌ Vehículo no encontrado")

def demo_drivers():
    """Demo: Operaciones con conductores"""
    print_section("👤 DEMO: Gestión de Conductores")
    
    # Listar conductores
    print("1️⃣ Listando conductores existentes...")
    response = requests.get(f"{API_V1}/drivers/")
    drivers = response.json()
    for d in drivers:
        print(f"   - {d['first_name']} {d['last_name']} (Licencia: {d['license_number']})")
    
    # Crear nuevo conductor
    print("\n2️⃣ Creando nuevo conductor...")
    new_driver = {
        "first_name": "Carlos",
        "last_name": "Martínez",
        "license_number": "D9876543"
    }
    response = requests.post(f"{API_V1}/drivers", json=new_driver)
    if response.status_code == 200:
        driver = response.json()
        print(f"   ✅ Conductor creado con ID: {driver['id']}")
        print(f"      - Nombre: {driver['first_name']} {driver['last_name']}")
        print(f"      - Licencia: {driver['license_number']}")
    else:
        print(f"   ❌ Error: {response.status_code}")

def demo_reservations():
    """Demo: Operaciones con reservas"""
    print_section("📅 DEMO: Gestión de Reservas")
    
    # Listar reservas
    print("1️⃣ Listando reservas existentes...")
    response = requests.get(f"{API_V1}/reservations/")
    reservations = response.json()
    for r in reservations:
        print(f"   - Reserva ID {r['id']}: Vehículo {r['vehicle_id']} - Conductor {r['driver_id']}")
        print(f"     Desde: {r['start_date']} Hasta: {r['end_date']}")
    
    # Crear nueva reserva
    print("\n2️⃣ Creando nueva reserva...")
    tomorrow = datetime.now() + timedelta(days=1)
    next_week = tomorrow + timedelta(days=7)
    
    new_reservation = {
        "vehicle_id": 1,
        "driver_id": 1,
        "start_date": tomorrow.isoformat(),
        "end_date": next_week.isoformat()
    }
    response = requests.post(f"{API_V1}/reservations", json=new_reservation)
    if response.status_code == 200:
        reservation = response.json()
        print(f"   ✅ Reserva creada con ID: {reservation['id']}")
        print(f"      - Vehículo: {reservation['vehicle_id']}")
        print(f"      - Conductor: {reservation['driver_id']}")
        print(f"      - Desde: {reservation['start_date']}")
        print(f"      - Hasta: {reservation['end_date']}")
    else:
        print(f"   ❌ Error: {response.status_code}")

def demo_api_info():
    """Demo: Información de la API"""
    print_section("ℹ️ DEMO: Información de la API")
    
    # Health check
    print("1️⃣ Verificando estado de la API...")
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"   ✅ API Status: {health['status']}")
        print(f"   Service: {health['service']}")
    
    # OpenAPI schema
    print("\n2️⃣ Contando endpoints disponibles...")
    response = requests.get(f"{API_BASE}/openapi.json")
    if response.status_code == 200:
        schema = response.json()
        endpoints = len(schema.get('paths', {}))
        print(f"   ✅ Total de endpoints: {endpoints}")
        print("\n   Endpoints disponibles:")
        for path in list(schema.get('paths', {}).keys())[:5]:
            print(f"      - {path}")
        if endpoints > 5:
            print(f"      ... y {endpoints - 5} más")

def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  🎯 DEMO: Sistema de Gestión de Flota de Vehículos")
    print("="*60)
    
    try:
        # Verify API is running
        response = requests.get(f"{API_BASE}/health", timeout=2)
        if response.status_code != 200:
            print("\n❌ API no está respondiendo. Ejecuta primero: python api_simple.py")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ No se puede conectar a la API en {API_BASE}. Asegúrate de que está ejecutándose.")
        print("   Ejecuta: python api_simple.py")
        return
    
    print("\n✅ API conectada y operativa")
    
    # Run demos
    demo_api_info()
    demo_vehicles()
    demo_drivers()
    demo_reservations()
    
    print_section("✅ Demo Completada")
    print("Para más información:")
    print("  - Documentación Swagger: http://localhost:8000/docs")
    print("  - Documentación ReDoc: http://localhost:8000/redoc")
    print("  - Schema OpenAPI: http://localhost:8000/openapi.json")
    print()

if __name__ == "__main__":
    main()
