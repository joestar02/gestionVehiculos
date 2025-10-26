from fastapi import APIRouter
from .endpoints import vehicles, drivers, reservations, organizations, auth, pickups, maintenance, compliance

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(pickups.router, prefix="/pickups", tags=["pickups"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
