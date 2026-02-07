"""
Simple FastAPI application for REST API endpoints
Independent of Flask to avoid import issues
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Sistema de Gestión de Flota de Vehículos",
    description="API REST para el Sistema de Gestión de Flota de Vehículos",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class VehicleBase(BaseModel):
    license_plate: str
    make: str
    model: str
    year: int

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DriverBase(BaseModel):
    first_name: str
    last_name: str
    license_number: str

class DriverCreate(DriverBase):
    pass

class Driver(DriverBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    vehicle_id: int
    driver_id: int
    start_date: datetime
    end_date: datetime

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Sample data
vehicles_db = [
    {
        "id": 1,
        "license_plate": "MAL-1234",
        "make": "Ford",
        "model": "Transit",
        "year": 2022,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "license_plate": "MAL-5678",
        "make": "Mercedes",
        "model": "Sprinter",
        "year": 2021,
        "created_at": datetime.now()
    }
]

drivers_db = [
    {
        "id": 1,
        "first_name": "Juan",
        "last_name": "García",
        "license_number": "D1234567",
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "first_name": "María",
        "last_name": "López",
        "license_number": "D7654321",
        "created_at": datetime.now()
    }
]

reservations_db = [
    {
        "id": 1,
        "vehicle_id": 1,
        "driver_id": 1,
        "start_date": datetime(2026, 2, 8),
        "end_date": datetime(2026, 2, 15),
        "created_at": datetime.now()
    }
]

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "API REST del Sistema de Gestión de Flota de Vehículos",
        "version": "1.0.0"
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vehicle-fleet-api"}

# Vehicles endpoints
@app.get("/api/v1/vehicles", response_model=List[Vehicle])
async def list_vehicles(skip: int = 0, limit: int = 10):
    """Get list of vehicles"""
    return vehicles_db[skip:skip + limit]

@app.get("/api/v1/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: int):
    """Get vehicle by ID"""
    for vehicle in vehicles_db:
        if vehicle["id"] == vehicle_id:
            return vehicle
    return {"detail": "Vehicle not found"}

@app.post("/api/v1/vehicles", response_model=Vehicle)
async def create_vehicle(vehicle: VehicleCreate):
    """Create a new vehicle"""
    new_id = max([v["id"] for v in vehicles_db]) + 1 if vehicles_db else 1
    new_vehicle = {
        "id": new_id,
        **vehicle.dict(),
        "created_at": datetime.now()
    }
    vehicles_db.append(new_vehicle)
    return new_vehicle

# Drivers endpoints
@app.get("/api/v1/drivers", response_model=List[Driver])
async def list_drivers(skip: int = 0, limit: int = 10):
    """Get list of drivers"""
    return drivers_db[skip:skip + limit]

@app.get("/api/v1/drivers/{driver_id}", response_model=Driver)
async def get_driver(driver_id: int):
    """Get driver by ID"""
    for driver in drivers_db:
        if driver["id"] == driver_id:
            return driver
    return {"detail": "Driver not found"}

@app.post("/api/v1/drivers", response_model=Driver)
async def create_driver(driver: DriverCreate):
    """Create a new driver"""
    new_id = max([d["id"] for d in drivers_db]) + 1 if drivers_db else 1
    new_driver = {
        "id": new_id,
        **driver.dict(),
        "created_at": datetime.now()
    }
    drivers_db.append(new_driver)
    return new_driver

# Reservations endpoints
@app.get("/api/v1/reservations", response_model=List[Reservation])
async def list_reservations(skip: int = 0, limit: int = 10):
    """Get list of reservations"""
    return reservations_db[skip:skip + limit]

@app.get("/api/v1/reservations/{reservation_id}", response_model=Reservation)
async def get_reservation(reservation_id: int):
    """Get reservation by ID"""
    for reservation in reservations_db:
        if reservation["id"] == reservation_id:
            return reservation
    return {"detail": "Reservation not found"}

@app.post("/api/v1/reservations", response_model=Reservation)
async def create_reservation(reservation: ReservationCreate):
    """Create a new reservation"""
    new_id = max([r["id"] for r in reservations_db]) + 1 if reservations_db else 1
    new_reservation = {
        "id": new_id,
        **reservation.dict(),
        "created_at": datetime.now()
    }
    reservations_db.append(new_reservation)
    return new_reservation

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
