"""Maintenance controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from app.utils.helpers import parse_money
from app.services.maintenance_service import MaintenanceService
from app.services.vehicle_service import VehicleService
from app.services.provider_service import ProviderService
from app.models.maintenance import MaintenanceType, MaintenanceStatus
from urllib.parse import urlencode
from app.utils.pagination import paginate_list



maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/')
@login_required
def list_maintenance():
    """List all maintenance records"""
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        per_page = 20

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('maintenance.list_maintenance')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    all_records = MaintenanceService.get_all_maintenance_records()
    records, pagination = paginate_list(all_records, page=page, per_page=per_page)
    return render_template('maintenance/list.html', records=records, pagination=pagination, base_list_url=base_list_url, preserved_qs=preserved_qs)

@maintenance_bp.route('/<int:record_id>')
@login_required
def view_maintenance(record_id):
    """View maintenance record details"""
    record = MaintenanceService.get_maintenance_by_id(record_id)
    if not record:
        flash('Registro de mantenimiento no encontrado', 'error')
        return redirect(url_for('maintenance.list_maintenance'))
    return render_template('maintenance/detail.html', record=record)

@maintenance_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_maintenance():
    """Create new maintenance record"""
    if request.method == 'POST':
        try:
            scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d')
            provider_id = int(request.form.get('provider_id')) if request.form.get('provider_id') else None
            estimated_cost = parse_money(request.form.get('estimated_cost'))

            record = MaintenanceService.create_maintenance(
                vehicle_id=int(request.form.get('vehicle_id')),
                maintenance_type=MaintenanceType(request.form.get('maintenance_type')),
                scheduled_date=scheduled_date,
                description=request.form.get('description'),
                estimated_cost=estimated_cost,
                provider_id=provider_id,
                notes=request.form.get('notes')
            )
            flash('Mantenimiento programado exitosamente', 'success')
            return redirect(url_for('maintenance.view_maintenance', record_id=record.id))
        except ValueError as ve:
            from app.utils.error_helpers import log_exception
            err_id = log_exception(ve, __name__)
            flash(f'Entrada inválida: {str(ve)} (id={err_id})', 'error')
        except Exception as e:
            from app.utils.error_helpers import log_exception
            err_id = log_exception(e, __name__)
            flash(f'Error al crear mantenimiento (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    providers = ProviderService.get_all_providers()
    return render_template('maintenance/form.html', 
                         maintenance_types=MaintenanceType,
                         vehicles=vehicles,
                         providers=providers)

@maintenance_bp.route('/<int:record_id>/complete', methods=['POST'])
@login_required
def complete_maintenance(record_id):
    """Complete maintenance"""
    try:
        actual_cost = parse_money(request.form.get('actual_cost'))
        completion_notes = request.form.get('completion_notes')

        record = MaintenanceService.complete_maintenance(record_id, actual_cost, completion_notes)
        if record:
            flash('Mantenimiento completado exitosamente', 'success')
        else:
            flash('Error al completar mantenimiento', 'error')
    except ValueError as ve:
        from app.utils.error_helpers import log_exception
        err_id = log_exception(ve, __name__)
        flash(f'Entrada inválida: {str(ve)} (id={err_id})', 'error')
    except Exception as e:
        from app.utils.error_helpers import log_exception
        err_id = log_exception(e, __name__)
        flash(f'Error: (id={err_id})', 'error')
    
    return redirect(url_for('maintenance.view_maintenance', record_id=record_id))


@maintenance_bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_maintenance(record_id):
    """Edit maintenance record"""
    record = MaintenanceService.get_maintenance_by_id(record_id)
    if not record:
        flash('Registro de mantenimiento no encontrado', 'error')
        return redirect(url_for('maintenance.list_maintenance'))

    if request.method == 'POST':
        try:
            scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d')
            provider_id = int(request.form.get('provider_id')) if request.form.get('provider_id') else None
            estimated_cost = parse_money(request.form.get('estimated_cost'))

            update_kwargs = dict(
                vehicle_id=int(request.form.get('vehicle_id')),
                maintenance_type=MaintenanceType(request.form.get('maintenance_type')),
                scheduled_date=scheduled_date,
                description=request.form.get('description'),
                estimated_cost=estimated_cost,
                provider_id=provider_id,
                notes=request.form.get('notes')
            )

            MaintenanceService.update_maintenance(record_id, **update_kwargs)
            flash('Registro de mantenimiento actualizado', 'success')
            return redirect(url_for('maintenance.view_maintenance', record_id=record_id))
        except Exception as e:
            from app.utils.error_helpers import log_exception
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar mantenimiento: (id={err_id})', 'error')

    vehicles = VehicleService.get_all_vehicles()
    providers = ProviderService.get_all_providers()
    return render_template('maintenance/form.html', maintenance_types=MaintenanceType, vehicles=vehicles, providers=providers, record=record)

@maintenance_bp.route('/<int:record_id>/cancel', methods=['POST'])
@login_required
def cancel_maintenance(record_id):
    """Cancel maintenance"""
    reason = request.form.get('cancellation_reason')
    if not reason:
        flash('Debe proporcionar un motivo de cancelación', 'error')
        return redirect(url_for('maintenance.view_maintenance', record_id=record_id))
    
    record = MaintenanceService.cancel_maintenance(record_id, reason)
    if record:
        flash('Mantenimiento cancelado exitosamente', 'success')
    else:
        flash('Error al cancelar mantenimiento', 'error')
    
    return redirect(url_for('maintenance.view_maintenance', record_id=record_id))
