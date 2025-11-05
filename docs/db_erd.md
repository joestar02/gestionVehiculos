# ERD - Base de datos (generado)

Este archivo contiene un diagrama ER en formato Mermaid extraído automáticamente de los modelos SQLAlchemy en `app/models/`.

```mermaid
erDiagram
    USERS {
        INTEGER id PK
        STRING email
        STRING username
    }

    ORGANIZATION_UNITS {
        INTEGER id PK
        STRING name
        STRING code
    }

    VEHICLES {
        INTEGER id PK
        STRING license_plate
        STRING vin
        INTEGER organization_unit_id FK
    }

    DRIVERS {
        INTEGER id PK
        STRING document_number
        STRING driver_license_number
        INTEGER organization_unit_id FK
    }

    VEHICLE_DRIVER_ASSOCIATIONS {
        INTEGER id PK
        INTEGER vehicle_id FK
        INTEGER driver_id FK
        DATETIME start_date
        DATETIME end_date
    }

    VEHICLE_ASSIGNMENTS {
        INTEGER id PK
        INTEGER vehicle_id FK
        INTEGER driver_id FK
        INTEGER organization_unit_id FK
        DATETIME start_date
        DATETIME end_date
    }

    RESERVATIONS {
        INTEGER id PK
        INTEGER vehicle_id FK
        INTEGER driver_id FK
        INTEGER user_id FK
        INTEGER organization_unit_id FK
        DATETIME start_date
        DATETIME end_date
    }

    VEHICLE_PICKUPS {
        INTEGER id PK
        INTEGER reservation_id FK
        INTEGER vehicle_id FK
        INTEGER driver_id FK
    }

    RENTING_CONTRACTS {
        INTEGER id PK
        INTEGER vehicle_id FK
        STRING contract_number
    }

    MAINTENANCE_RECORDS {
        INTEGER id PK
        INTEGER vehicle_id FK
        INTEGER provider_id FK
    }

    PROVIDERS {
        INTEGER id PK
        STRING name
    }

    ITV_RECORDS {
        INTEGER id PK
        INTEGER vehicle_id FK
        DATETIME inspection_date
    }

    VEHICLE_TAXES {
        INTEGER id PK
        INTEGER vehicle_id FK
        INTEGER tax_year
    }

    VEHICLE_INSURANCES {
        INTEGER id PK
        INTEGER vehicle_id FK
        STRING policy_number
    }

    FINES {
        INTEGER id PK
        INTEGER vehicle_id FK
        INTEGER driver_id FK
        STRING fine_number
    }

    URBAN_ACCESS_AUTHORIZATIONS {
        INTEGER id PK
        INTEGER vehicle_id FK
        STRING authorization_number
    }

    ACCIDENTS {
        INTEGER id PK
        INTEGER vehicle_id FK
        INTEGER driver_id FK
    }

    # Relaciones (one-to-many where left side is the parent)
    ORGANIZATION_UNITS ||--o{ VEHICLES : "contains"
    ORGANIZATION_UNITS ||--o{ DRIVERS : "contains"
    ORGANIZATION_UNITS ||--o{ VEHICLE_ASSIGNMENTS : "owns"

    VEHICLES ||--o{ VEHICLE_DRIVER_ASSOCIATIONS : "has_associations"
    DRIVERS ||--o{ VEHICLE_DRIVER_ASSOCIATIONS : "has_associations"

    VEHICLES ||--o{ VEHICLE_ASSIGNMENTS : "has_assignments"
    DRIVERS ||--o{ VEHICLE_ASSIGNMENTS : "has_assignments"

    VEHICLES ||--o{ RESERVATIONS : "has_reservations"
    DRIVERS ||--o{ RESERVATIONS : "has_reservations"
    USERS ||--o{ RESERVATIONS : "creates"

    RESERVATIONS ||--o{ VEHICLE_PICKUPS : "may_have"
    VEHICLES ||--o{ VEHICLE_PICKUPS : "pickups"
    DRIVERS ||--o{ VEHICLE_PICKUPS : "pickups"

    VEHICLES ||--o{ RENTING_CONTRACTS : "renting_contracts"
    VEHICLES ||--o{ MAINTENANCE_RECORDS : "maintenance_records"
    PROVIDERS ||--o{ MAINTENANCE_RECORDS : "provides"

    VEHICLES ||--o{ ITV_RECORDS : "itv_records"
    VEHICLES ||--o{ VEHICLE_TAXES : "taxes"
    VEHICLES ||--o{ VEHICLE_INSURANCES : "insurances"
    VEHICLES ||--o{ FINES : "fines"
    VEHICLES ||--o{ URBAN_ACCESS_AUTHORIZATIONS : "authorizations"
    VEHICLES ||--o{ ACCIDENTS : "accidents"

    USERS ||--o{ VEHICLE_DRIVER_ASSOCIATIONS : "creates"
    USERS ||--o{ VEHICLE_ASSIGNMENTS : "creates"
    USERS ||--o{ MAINTENANCE_RECORDS : "creates"
    USERS ||--o{ FINES : "creates"
```

Notas:
- El diagrama está pensado para lectura rápida y no incluye todos los campos ni índices.
- Si quieres que lo exporte a PNG o SVG (PlantUML/Graphviz), dime si tienes Graphviz/PlantUML instalado en tu máquina; puedo generar un `docs/db_erd.puml` o un `.dot` y tratar de renderizarlo aquí.
