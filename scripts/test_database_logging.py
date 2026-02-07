#!/usr/bin/env python3
"""
Script de prueba para verificar el logging de base de datos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import create_app
from app.services.vehicle_service import VehicleService
from app.services.auth_service import AuthService
from app.services.reservation_service import ReservationService
from app.models.vehicle import VehicleType, OwnershipType
from datetime import datetime, timedelta

def test_database_logging():
    """Prueba el logging de operaciones de base de datos"""
    app = create_app()

    with app.app_context():
        print("🧪 Probando logging de base de datos...")

        # 1. Crear un usuario de prueba
        print("\n1. Creando usuario de prueba...")
        try:
            test_user = AuthService.create_user(
                username="test_audit_user",
                email="test_audit@example.com",
                password="testpass123",
                first_name="Test",
                last_name="Audit"
            )
            print(f"✅ Usuario creado: {test_user.username} (ID: {test_user.id})")
        except ValueError as e:
            print(f"⚠️ Usuario ya existe: {e}")
            test_user = AuthService.get_user_by_username("test_audit_user")

        # 2. Crear un vehículo de prueba
        print("\n2. Creando vehículo de prueba...")
        vehicle = VehicleService.create_vehicle(
            license_plate="AUDIT-001",
            make="TestMake",
            model="TestModel",
            year=2023,
            vehicle_type=VehicleType.CAR,
            ownership_type=OwnershipType.OWNED,
            color="Blue",
            notes="Vehículo de prueba para auditoría"
        )
        print(f"✅ Vehículo creado: {vehicle.license_plate} (ID: {vehicle.id})")

        # 3. Actualizar el vehículo
        print("\n3. Actualizando vehículo...")
        updated_vehicle = VehicleService.update_vehicle(
            vehicle.id,
            color="Red",
            notes="Vehículo de prueba actualizado"
        )
        print(f"✅ Vehículo actualizado: {vehicle.license_plate}")

        # 4. Crear una reserva
        print("\n4. Creando reserva...")
        start_date = datetime.utcnow() + timedelta(days=1)
        end_date = start_date + timedelta(hours=2)

        reservation = ReservationService.create_reservation(
            vehicle_id=vehicle.id,
            driver_id=1,  # Asumiendo que existe un driver con ID 1
            start_date=start_date,
            end_date=end_date,
            purpose="Prueba de auditoría",
            user_id=test_user.id,
            destination="Oficina central",
            notes="Reserva de prueba para verificar logging"
        )
        print(f"✅ Reserva creada: ID {reservation.id}")

        # 5. Confirmar la reserva
        print("\n5. Confirmando reserva...")
        confirmed_reservation = ReservationService.confirm_reservation(reservation.id)
        print(f"✅ Reserva confirmada: ID {reservation.id}")

        # 6. Cancelar la reserva
        print("\n6. Cancelando reserva...")
        cancelled_reservation = ReservationService.cancel_reservation(
            reservation.id,
            "Cancelación de prueba para auditoría"
        )
        print(f"✅ Reserva cancelada: ID {reservation.id}")

        # 7. Eliminar el vehículo (soft delete)
        print("\n7. Eliminando vehículo...")
        VehicleService.delete_vehicle(vehicle.id)
        print(f"✅ Vehículo eliminado (soft delete): {vehicle.license_plate}")

        print("\n🎉 Todas las operaciones completadas exitosamente!")
        print("📋 Revisa los logs de auditoría para verificar que todas las operaciones fueron registradas.")
        print("   - Logs de seguridad: logs/security_audit.log")
        print("   - Logs de base de datos: logs/database_operations.log")

if __name__ == "__main__":
    test_database_logging()