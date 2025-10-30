"""
Script para recrear la base de datos con la estructura actualizada
ADVERTENCIA: Este script eliminará todos los datos existentes
"""
import os
from app.main import create_app
from app.extensions import db

def recreate_database():
    """Recrear la base de datos desde cero"""
    app = create_app()
    
    with app.app_context():
        # Ruta de la base de datos
        db_path = 'gestion_vehiculos.db'
        
        print("🔄 Recreando base de datos...")
        print(f"📁 Archivo: {db_path}")
        
        # Eliminar base de datos existente
        if os.path.exists(db_path):
            print("❌ Eliminando base de datos antigua...")
            os.remove(db_path)
            print("✅ Base de datos antigua eliminada")
        
        # Crear todas las tablas
        print("🔨 Creando nuevas tablas...")
        db.create_all()
        print("✅ Tablas creadas exitosamente")
        
        # Crear usuario administrador por defecto
        from app.models import User, UserRole
        from werkzeug.security import generate_password_hash
        
        print("👤 Creando usuario administrador...")
        admin = User(
            username="admin",
            email="admin@juntadeandalucia.es",
            full_name="Administrador del Sistema",
            password_hash=generate_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.session.add(admin)
        
        # Crear usuario de prueba
        user = User(
            username="usuario",
            email="usuario@juntadeandalucia.es",
            full_name="Usuario de Prueba",
            password_hash=generate_password_hash("usuario123"),
            role=UserRole.USER,
            is_active=True
        )
        db.session.add(user)
        
        db.session.commit()
        print("✅ Usuarios creados:")
        print("   - admin / admin123 (Administrador)")
        print("   - usuario / usuario123 (Usuario)")
        
        # Mostrar tablas creadas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in sorted(tables):
            print(f"   ✓ {table}")
        
        print("\n✅ Base de datos recreada exitosamente!")
        print("🚀 Puedes iniciar la aplicación con: python run.py")

if __name__ == "__main__":
    print("=" * 60)
    print("RECREAR BASE DE DATOS - Sistema de Gestión de Flota")
    print("Junta de Andalucía")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Este script eliminará TODOS los datos existentes")
    
    respuesta = input("\n¿Estás seguro de que deseas continuar? (si/no): ")
    
    if respuesta.lower() in ['si', 's', 'yes', 'y']:
        recreate_database()
    else:
        print("❌ Operación cancelada")
