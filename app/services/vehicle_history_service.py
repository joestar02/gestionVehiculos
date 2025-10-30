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
            # ensure a valid date for sorting/display
            assign_date = assignment.start_date or getattr(assignment, 'created_at', datetime.utcnow())
            end_str = assignment.end_date.strftime('%d/%m/%Y') if getattr(assignment, 'end_date', None) else 'Actualidad'
            history.append({
                'type': 'assignment',
                'date': assign_date,
                'title': f'Asignación a {assignment.driver.full_name if assignment.driver else "conductor desconocido"}',
                'details': f"Desde: {assign_date.strftime('%d/%m/%Y')} - "
                         f"Hasta: {end_str}",
                'icon': 'bi-person-badge',
                'class': 'text-primary'
            })
        
        # Get maintenance records
        maintenances = Maintenance.query.filter_by(vehicle_id=vehicle_id).order_by(Maintenance.scheduled_date.desc()).all()
        for maintenance in maintenances:
            maint_date = maintenance.scheduled_date or getattr(maintenance, 'created_at', datetime.utcnow())
            cost_str = maintenance.cost or 'N/A'
            history.append({
                'type': 'maintenance',
                'date': maint_date,
                'title': f'Mantenimiento: {maintenance.maintenance_type}',
                'details': f"{maintenance.description if maintenance.description else 'Sin descripción'}. "
                         f"Costo: {cost_str}",
                'icon': 'bi-tools',
                'class': 'text-warning'
            })
        
        # Get insurance records
        insurances = Insurance.query.filter_by(vehicle_id=vehicle_id).order_by(Insurance.start_date.desc()).all()
        for insurance in insurances:
            ins_date = insurance.start_date or getattr(insurance, 'created_at', datetime.utcnow())
            end_str = insurance.end_date.strftime('%d/%m/%Y') if getattr(insurance, 'end_date', None) else 'No especificado'
            history.append({
                'type': 'insurance',
                'date': ins_date,
                'title': 'Seguro',
                'details': f"Compañía: {insurance.insurance_company}. "
                         f"Válido hasta: {end_str}",
                'icon': 'bi-shield-check',
                'class': 'text-success'
            })
        
        # Get inspections (ITV)
        inspections = Inspection.query.filter_by(vehicle_id=vehicle_id).order_by(Inspection.inspection_date.desc()).all()
        for inspection in inspections:
            insp_date = inspection.inspection_date or getattr(inspection, 'created_at', datetime.utcnow())
            next_str = inspection.next_inspection_date.strftime('%d/%m/%Y') if getattr(inspection, 'next_inspection_date', None) else 'No especificada'
            history.append({
                'type': 'inspection',
                'date': insp_date,
                'title': 'Inspección Técnica (ITV)',
                'details': f"Resultado: {inspection.result}. "
                         f"Próxima: {next_str}",
                'icon': 'bi-clipboard-check',
                'class': 'text-info'
            })
        
        # Get tax records
        taxes = Tax.query.filter_by(vehicle_id=vehicle_id).order_by(Tax.due_date.desc()).all()
        for tax in taxes:
            tax_date = tax.due_date or getattr(tax, 'created_at', datetime.utcnow())
            # VehicleTax model stores amount (Numeric) and payment_status (Enum). There is no currency field.
            amount_str = f"€{float(tax.amount):.2f}" if tax.amount is not None else 'N/A'
            status_str = tax.payment_status.value if getattr(tax, 'payment_status', None) is not None else 'N/A'
            history.append({
                'type': 'tax',
                'date': tax_date,
                'title': 'Impuesto de Vehículo',
                'details': f"Importe: {amount_str}. "
                         f"Estado: {status_str}",
                'icon': 'bi-cash-stack',
                'class': 'text-danger'
            })
        
        # Get fines
        fines = Fine.query.filter_by(vehicle_id=vehicle_id).order_by(Fine.fine_date.desc()).all()
        for fine in fines:
            fine_date = fine.fine_date or getattr(fine, 'created_at', datetime.utcnow())
            amount_str = f"€{float(fine.amount):.2f}" if fine.amount is not None else 'N/A'
            status_str = fine.status.value if getattr(fine, 'status', None) is not None else 'N/A'
            history.append({
                'type': 'fine',
                'date': fine_date,
                'title': 'Multa de Tráfico',
                'details': f"Importe: {amount_str}. "
                         f"Estado: {status_str}",
                'icon': 'bi-exclamation-triangle',
                'class': 'text-danger'
            })
        
        # Get authorizations
        authorizations = Authorization.query.filter_by(vehicle_id=vehicle_id).order_by(Authorization.start_date.desc()).all()
        for auth in authorizations:
            # The model does not store an "authorized_person" field. Use available fields instead.
            auth_type = auth.authorization_type or 'N/D'
            auth_number = auth.authorization_number or 'N/D'
            issuing = auth.issuing_authority or 'N/D'
            zone = auth.zone_description or ''
            end_date_str = auth.end_date.strftime('%d/%m/%Y') if auth.end_date else 'Sin fecha de fin'
            details_parts = [f"Tipo: {auth_type}", f"Nº: {auth_number}", f"Emitido por: {issuing}"]
            if zone:
                details_parts.append(f"Zona: {zone}")
            details_parts.append(f"Hasta: {end_date_str}")
            history.append({
                'type': 'authorization',
                'date': auth.start_date,
                'title': 'Autorización de Uso',
                'details': ' / '.join(details_parts),
                'icon': 'bi-file-earmark-check',
                'class': 'text-success'
            })
        
        # Sort all history by date in descending order
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return history
