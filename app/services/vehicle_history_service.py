"""Vehicle history service"""
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import or_
from app.extensions import db
from app.models.vehicle import Vehicle
from app.models.vehicle_assignment import VehicleAssignment as Assignment
from app.models.maintenance import MaintenanceRecord as Maintenance
from app.models.insurance import VehicleInsurance as Insurance
from app.models.itv import ITVRecord as Inspection
from app.models.tax import VehicleTax as Tax
from app.models.fine import Fine
from app.models.authorization import UrbanAccessAuthorization as Authorization

class VehicleHistoryService:
    """Service for vehicle history operations"""
    
    @staticmethod
    def get_vehicle_history(vehicle_id: int) -> List[Dict[str, Any]]:
        """Get all history records for a vehicle"""
        history = []
        
        # Get assignments
        assignments = Assignment.query.filter_by(vehicle_id=vehicle_id).order_by(Assignment.start_date.desc()).all()
        for assignment in assignments:
            history.append({
                'type': 'assignment',
                'date': assignment.start_date,
                'title': f'Asignación a {assignment.driver.full_name if assignment.driver else "conductor desconocido"}',
                'details': f"Desde: {assignment.start_date.strftime('%d/%m/%Y')} - "
                         f"Hasta: {assignment.end_date.strftime('%d/%m/%Y') if assignment.end_date else 'Actualidad'}",
                'icon': 'bi-person-badge',
                'class': 'text-primary'
            })
        
        # Get maintenance records
        maintenances = Maintenance.query.filter_by(vehicle_id=vehicle_id).order_by(Maintenance.scheduled_date.desc()).all()
        for maintenance in maintenances:
            history.append({
                'type': 'maintenance',
                'date': maintenance.scheduled_date,
                'title': f'Mantenimiento: {maintenance.maintenance_type}',
                'details': f"{maintenance.description if maintenance.description else 'Sin descripción'}. "
                         f"Costo: {maintenance.cost or 'N/A'}",
                'icon': 'bi-tools',
                'class': 'text-warning'
            })
        
        # Get insurance records
        insurances = Insurance.query.filter_by(vehicle_id=vehicle_id).order_by(Insurance.start_date.desc()).all()
        for insurance in insurances:
            history.append({
                'type': 'insurance',
                'date': insurance.start_date,
                'title': 'Seguro',
                'details': f"Compañía: {insurance.insurance_company}. "
                         f"Válido hasta: {insurance.end_date.strftime('%d/%m/%Y') if insurance.end_date else 'No especificado'}",
                'icon': 'bi-shield-check',
                'class': 'text-success'
            })
        
        # Get inspections (ITV)
        inspections = Inspection.query.filter_by(vehicle_id=vehicle_id).order_by(Inspection.inspection_date.desc()).all()
        for inspection in inspections:
            history.append({
                'type': 'inspection',
                'date': inspection.inspection_date,
                'title': 'Inspección Técnica (ITV)',
                'details': f"Resultado: {inspection.result}. "
                         f"Próxima: {inspection.next_inspection_date.strftime('%d/%m/%Y') if inspection.next_inspection_date else 'No especificada'}",
                'icon': 'bi-clipboard-check',
                'class': 'text-info'
            })
        
        # Get tax records
        taxes = Tax.query.filter_by(vehicle_id=vehicle_id).order_by(Tax.due_date.desc()).all()
        for tax in taxes:
            history.append({
                'type': 'tax',
                'date': tax.due_date,
                'title': 'Impuesto de Vehículo',
                'details': f"Importe: {tax.amount} {tax.currency}. "
                         f"Estado: {tax.status}",
                'icon': 'bi-cash-stack',
                'class': 'text-danger'
            })
        
        # Get fines
        fines = Fine.query.filter_by(vehicle_id=vehicle_id).order_by(Fine.fine_date.desc()).all()
        for fine in fines:
            history.append({
                'type': 'fine',
                'date': fine.fine_date,
                'title': 'Multa de Tráfico',
                'details': f"Importe: {fine.amount} {fine.currency}. "
                         f"Estado: {fine.status}",
                'icon': 'bi-exclamation-triangle',
                'class': 'text-danger'
            })
        
        # Get authorizations
        authorizations = Authorization.query.filter_by(vehicle_id=vehicle_id).order_by(Authorization.start_date.desc()).all()
        for auth in authorizations:
            history.append({
                'type': 'authorization',
                'date': auth.start_date,
                'title': 'Autorización de Uso',
                'details': f"Autorizado para: {auth.authorized_person}. "
                         f"Hasta: {auth.end_date.strftime('%d/%m/%Y') if auth.end_date else 'Sin fecha de fin'}",
                'icon': 'bi-file-earmark-check',
                'class': 'text-success'
            })
        
        # Sort all history by date in descending order
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return history
