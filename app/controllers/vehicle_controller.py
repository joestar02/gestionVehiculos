"""Vehicle controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.vehicle_service import VehicleService
from app.models.vehicle import VehicleType, OwnershipType, VehicleStatus
from app.utils.error_helpers import log_exception

vehicle_bp = Blueprint('vehicles', __name__)

@vehicle_bp.route('/')
@login_required
def list_vehicles():
    """List all vehicles"""
    vehicles = VehicleService.get_all_vehicles()
    return render_template('vehicles/list.html', vehicles=vehicles)

@vehicle_bp.route('/<int:vehicle_id>')
@login_required
def view_vehicle(vehicle_id):
    """View vehicle details"""
    from app.services.vehicle_history_service import VehicleHistoryService
    
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        flash('Vehículo no encontrado', 'error')
        return redirect(url_for('vehicles.list_vehicles'))
    
    # Get vehicle history
    history = VehicleHistoryService.get_vehicle_history(vehicle_id)
    
    return render_template('vehicles/detail.html', 
                         vehicle=vehicle, 
                         history=history,
                         history_by_type={
                             'all': history,
                             'assignments': [h for h in history if h['type'] == 'assignment'],
                             'maintenance': [h for h in history if h['type'] == 'maintenance'],
                             'insurance': [h for h in history if h['type'] == 'insurance'],
                             'inspection': [h for h in history if h['type'] == 'inspection'],
                             'tax': [h for h in history if h['type'] == 'tax'],
                             'fine': [h for h in history if h['type'] == 'fine'],
                             'authorization': [h for h in history if h['type'] == 'authorization']
                         })

@vehicle_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_vehicle():
    """Create new vehicle"""
    if request.method == 'POST':
        try:
            vehicle = VehicleService.create_vehicle(
                license_plate=request.form.get('license_plate'),
                make=request.form.get('make'),
                model=request.form.get('model'),
                year=int(request.form.get('year')),
                vehicle_type=VehicleType(request.form.get('vehicle_type')),
                ownership_type=OwnershipType(request.form.get('ownership_type')),
                color=request.form.get('color'),
                vin=request.form.get('vin'),
                fuel_type=request.form.get('fuel_type'),
                fuel_capacity=int(request.form.get('fuel_capacity')) if request.form.get('fuel_capacity') else None,
                notes=request.form.get('notes')
            )
            flash(f'Vehículo {vehicle.license_plate} creado exitosamente', 'success')
            return redirect(url_for('vehicles.view_vehicle', vehicle_id=vehicle.id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear vehículo (id={err_id})', 'error')
    
    return render_template('vehicles/form.html', 
                         vehicle_types=VehicleType,
                         ownership_types=OwnershipType)

@vehicle_bp.route('/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    """Edit vehicle"""
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        flash('Vehículo no encontrado', 'error')
        return redirect(url_for('vehicles.list_vehicles'))
    
    if request.method == 'POST':
        try:
            update_data = {
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'year': int(request.form.get('year')),
                'color': request.form.get('color'),
                'vin': request.form.get('vin'),
                'vehicle_type': VehicleType(request.form.get('vehicle_type')),
                'ownership_type': OwnershipType(request.form.get('ownership_type')),
                'fuel_type': request.form.get('fuel_type'),
                'notes': request.form.get('notes')
            }
            
            if request.form.get('fuel_capacity'):
                update_data['fuel_capacity'] = int(request.form.get('fuel_capacity'))
            
            VehicleService.update_vehicle(vehicle_id, **update_data)
            flash('Vehículo actualizado exitosamente', 'success')
            return redirect(url_for('vehicles.view_vehicle', vehicle_id=vehicle_id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar vehículo (id={err_id})', 'error')
    
    return render_template('vehicles/form.html', 
                         vehicle=vehicle,
                         vehicle_types=VehicleType,
                         ownership_types=OwnershipType)

@vehicle_bp.route('/<int:vehicle_id>/delete', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    """Delete vehicle"""
    if VehicleService.delete_vehicle(vehicle_id):
        flash('Vehículo eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar vehículo', 'error')
    return redirect(url_for('vehicles.list_vehicles'))

@vehicle_bp.route('/<int:vehicle_id>/status', methods=['POST'])
@login_required
def update_status(vehicle_id):
    """Update vehicle status"""
    try:
        status = VehicleStatus(request.form.get('status'))
        vehicle = VehicleService.update_vehicle_status(vehicle_id, status)
        if vehicle:
            flash(f'Estado del vehículo actualizado a {status.value}', 'success')
        else:
            flash('Vehículo no encontrado', 'error')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al actualizar estado (id={err_id})', 'error')
    
    return redirect(url_for('vehicles.view_vehicle', vehicle_id=vehicle_id))

@vehicle_bp.route('/search')
@login_required
def search_vehicles():
    """Search vehicles"""
    search_term = request.args.get('q', '')
    if search_term:
        vehicles = VehicleService.search_vehicles(search_term)
    else:
        vehicles = VehicleService.get_all_vehicles()
    
    return render_template('vehicles/list.html', vehicles=vehicles, search_term=search_term)
