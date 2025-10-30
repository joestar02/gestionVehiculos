from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.utils.helpers import parse_money
from app.utils.error_helpers import log_exception
from app.services.vehicle_service import VehicleService
from app.services.driver_service import DriverService
from app.services.vehicle_transfer_service import VehicleTransferService
from app.models.vehicle_assignment import VehicleAssignment, AssignmentType, PaymentStatus
from app.models.user import UserRole

vehicle_transfer_bp = Blueprint('vehicle_transfers', __name__, url_prefix='/vehicle-transfers')

@vehicle_transfer_bp.route('/')
@login_required
def list_transfers():
    """List all vehicle transfers"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    records = VehicleTransferService.get_all_transfers()
    return render_template('vehicle_transfers/list.html', records=records)

@vehicle_transfer_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_transfer():
    """Create new vehicle transfer"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
            
            transfer = VehicleTransferService.create_transfer(
                vehicle_id=int(request.form.get('vehicle_id')),
                driver_id=int(request.form.get('driver_id')),
                assignment_type=AssignmentType(request.form.get('assignment_type')),
                start_date=start_date,
                end_date=end_date,
                assignment_fee=parse_money(request.form.get('assignment_fee') or '0'),
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes'),
                created_by=current_user.id
            )
            
            flash('Cesión creada exitosamente', 'success')
            return redirect(url_for('vehicle_transfers.view_transfer', transfer_id=transfer.id))
            
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear la cesión (id={err_id})', 'error')
    
    # Get all vehicles and drivers for the form
    vehicles = VehicleService.get_all_vehicles()
    drivers = DriverService.get_active_drivers()
    
    return render_template('vehicle_transfers/form.html',
                         vehicles=vehicles,
                         drivers=drivers,
                         assignment_types=AssignmentType)

@vehicle_transfer_bp.route('/<int:transfer_id>')
@login_required
def view_transfer(transfer_id):
    """View vehicle transfer details"""
    transfer = VehicleTransferService.get_transfer_by_id(transfer_id)
    if not transfer:
        flash('Cesión no encontrada', 'error')
        return redirect(url_for('vehicle_transfers.list_transfers'))
        
    return render_template('vehicle_transfers/detail.html', transfer=transfer)

@vehicle_transfer_bp.route('/<int:transfer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transfer(transfer_id):
    """Edit vehicle transfer"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    transfer = VehicleTransferService.get_transfer_by_id(transfer_id)
    if not transfer:
        flash('Cesión no encontrada', 'error')
        return redirect(url_for('vehicle_transfers.list_transfers'))

    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
            
            VehicleTransferService.update_transfer(
                transfer_id=transfer_id,
                vehicle_id=int(request.form.get('vehicle_id')),
                driver_id=int(request.form.get('driver_id')),
                assignment_type=AssignmentType(request.form.get('assignment_type')),
                start_date=start_date,
                end_date=end_date,
                assignment_fee=parse_money(request.form.get('assignment_fee') or '0'),
                purpose=request.form.get('purpose'),
                destination=request.form.get('destination'),
                notes=request.form.get('notes')
            )
            
            flash('Cesión actualizada exitosamente', 'success')
            return redirect(url_for('vehicle_transfers.view_transfer', transfer_id=transfer_id))
            
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar la cesión (id={err_id})', 'error')
    
    # Get all vehicles and drivers for the form
    vehicles = VehicleService.get_all_vehicles()
    drivers = DriverService.get_active_drivers()
    
    return render_template('vehicle_transfers/form.html',
                         transfer=transfer,
                         vehicles=vehicles,
                         drivers=drivers,
                         assignment_types=AssignmentType)

@vehicle_transfer_bp.route('/<int:transfer_id>/delete', methods=['POST'])
@login_required
def delete_transfer(transfer_id):
    """Delete vehicle transfer"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FLEET_MANAGER]:
        flash('Acceso denegado.', 'error')
        return redirect(url_for('main.index'))

    try:
        VehicleTransferService.delete_transfer(transfer_id)
        flash('Cesión eliminada exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar la cesión (id={err_id})', 'error')
        
    return redirect(url_for('vehicle_transfers.list_transfers'))
