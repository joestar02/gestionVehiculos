"""
Script para resetear la base de datos
Este script renombra la BD antigua y crea una nueva
"""
import os
import shutil
from datetime import datetime
from app.main import create_app
from app.extensions import db

def reset_database():
    """Resetear la base de datos"""
    app = create_app()
    
    with app.app_context():
        db_path = 'gestion_vehiculos.db'
        
        print("🔄 Reseteando base de datos...")
        
        # Hacer backup de la BD antigua si existe
        if os.path.exists(db_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'gestion_vehiculos_backup_{timestamp}.db'
            
            try:
                print(f"💾 Creando backup: {backup_path}")
                shutil.copy2(db_path, backup_path)
                print("✅ Backup creado")
                
                print("❌ Intentando eliminar BD antigua...")
                os.remove(db_path)
                print("✅ BD antigua eliminada")
            except PermissionError:
                print("⚠️  No se puede eliminar la BD (está en uso)")
                print("📝 INSTRUCCIONES:")
                print("   1. Detén la aplicación (Ctrl+C en la terminal donde corre)")
                print("   2. Ejecuta este script nuevamente")
                print("   3. O elimina manualmente: gestion_vehiculos.db")
                return False
        
        # Crear todas las tablas
        print("🔨 Creando nuevas tablas...")
        db.create_all()
        print("✅ Tablas creadas")
        
        # Crear usuarios
        from app.models import User, UserRole
        from app.services.auth_service import AuthService
        
        print("👤 Creando usuarios...")
        
        # Usar el servicio de autenticación para crear usuarios
        admin = AuthService.create_user(
            username="admin",
            email="admin@juntadeandalucia.es",
            password="admin123",
            first_name="Administrador",
            last_name="del Sistema",
            role=UserRole.ADMIN
        )
        admin.is_superuser = True
        
        user = AuthService.create_user(
            username="usuario",
            email="usuario@juntadeandalucia.es",
            password="usuario123",
            first_name="Usuario",
            last_name="de Prueba",
            role=UserRole.VIEWER
        )
        
        db.session.commit()
        
        print("✅ Usuarios creados:")
        print("   📧 admin / admin123 (Administrador)")
        print("   📧 usuario / usuario123 (Usuario)")
        
        # Mostrar tablas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in sorted(tables):
            print(f"   ✓ {table}")
        
        print("\n" + "="*60)
        print("✅ BASE DE DATOS RESETEADA EXITOSAMENTE")
        print("="*60)
        print("\n🚀 Inicia la aplicación con: python run.py")
        print("🌐 Accede a: http://localhost:5000")
        print("🔑 Login: admin / admin123\n")
        
        return True

if __name__ == "__main__":
    print("="*60)
    print("RESETEAR BASE DE DATOS")
    print("Sistema de Gestión de Flota - Junta de Andalucía")
    print("="*60)
    
    if reset_database():
        print("\n✅ Proceso completado con éxito")
    else:
        print("\n❌ Proceso interrumpido")
        print("\n💡 SOLUCIÓN RÁPIDA:")
        print("   1. Cierra la aplicación si está corriendo")
        print("   2. Elimina manualmente: gestion_vehiculos.db")
        print("   3. Ejecuta: python run.py")
        print("   (La aplicación creará la BD automáticamente)")
