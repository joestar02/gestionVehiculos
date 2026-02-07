# Permission definitions and role assignments
from app.models.user import UserRole

PERMISSIONS = {
    # Vehicle permissions
    "vehicle:view": "Ver vehículos",
    "vehicle:create": "Crear vehículos",
    "vehicle:edit": "Editar vehículos",
    "vehicle:delete": "Eliminar vehículos",

    # Reservation permissions
    "reservation:view": "Ver reservas",
    "reservation:create": "Crear reservas",
    "reservation:edit": "Editar reservas",
    "reservation:cancel": "Cancelar reservas",

    # Driver permissions
    "driver:view": "Ver conductores",
    "driver:create": "Crear conductores",
    "driver:edit": "Editar conductores",

    # Assignment permissions
    "assignment:view": "Ver asignaciones",
    "assignment:create": "Crear asignaciones",
    "assignment:edit": "Editar asignaciones",

    # Maintenance permissions
    "maintenance:view": "Ver mantenimientos",
    "maintenance:create": "Crear mantenimientos",
    "maintenance:edit": "Editar mantenimientos",

    # Provider permissions
    "provider:view": "Ver proveedores",
    "provider:create": "Crear proveedores",
    "provider:edit": "Editar proveedores",

    # Organization permissions
    "organization:view": "Ver organizaciones",
    "organization:create": "Crear organizaciones",
    "organization:edit": "Editar organizaciones",

    # User management
    "user:view": "Ver usuarios",
    "user:create": "Crear usuarios",
    "user:edit": "Editar usuarios",

    # Reports and analytics
    "report:view": "Ver reportes",
    "report:create": "Crear reportes",
}

ROLE_PERMISSIONS = {
    UserRole.ADMIN: list(PERMISSIONS.keys()),  # All permissions

    UserRole.FLEET_MANAGER: [
        "vehicle:view", "vehicle:create", "vehicle:edit",
        "reservation:view", "reservation:create", "reservation:edit", "reservation:cancel",
        "assignment:view", "assignment:create", "assignment:edit",
        "driver:view", "driver:create", "driver:edit",
        "maintenance:view", "maintenance:create", "maintenance:edit",
        "provider:view", "provider:create", "provider:edit",
        "organization:view", "organization:create", "organization:edit",
        "report:view", "report:create",
    ],

    UserRole.OPERATIONS_MANAGER: [
        "vehicle:view", "vehicle:create", "vehicle:edit",
        "reservation:view", "reservation:create", "reservation:edit", "reservation:cancel",
        "assignment:view", "assignment:create", "assignment:edit",
        "driver:view", "driver:create", "driver:edit",
        "provider:view", "provider:create", "provider:edit",
        "organization:view",
        "report:view",
    ],

    UserRole.DRIVER: [
        "vehicle:view",
        "reservation:view", "reservation:create",  # Only their own
        "assignment:view",  # Only their own
        "maintenance:view",  # Related to their vehicles
    ],

    UserRole.VIEWER: [
        "vehicle:view",
        "reservation:view",
        "assignment:view",
        "driver:view",
        "maintenance:view",
        "provider:view",
        "organization:view",
        "report:view",
    ],
}