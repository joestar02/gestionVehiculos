from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import logging
import uuid
from app.utils.exceptions import UploadError
from flask_login import login_required, current_user
from datetime import datetime
from app.services.itv_service import ITVService
from app.services.tax_service import TaxService
from app.services.fine_service import FineService
from app.services.authorization_service import AuthorizationService
from app.services.vehicle_service import VehicleService
from app.services.insurance_service import InsuranceService
from app.utils.helpers import save_uploaded_file, parse_money
from app.utils.error_helpers import log_exception
from app.models.itv import ITVResult, ITVStatus
from app.models.tax import TaxType, PaymentStatus
from app.models.insurance import InsuranceType
from app.models.fine import FineType, FineStatus

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/')
@login_required
def compliance_dashboard():
    """Compliance dashboard"""
    # Get statistics
    expired_itvs = ITVService.get_expired_itvs()
    expiring_itvs = ITVService.get_expiring_soon(30)
    pending_taxes = TaxService.get_pending_taxes()
    overdue_taxes = TaxService.get_overdue_taxes()
    pending_fines = FineService.get_pending_fines()
    overdue_fines = FineService.get_overdue_fines()
    # Get insurance statistics
    expiring_insurances = InsuranceService.get_expiring_soon_insurances(30)
    expired_insurances = InsuranceService.get_expired_insurances()
    pending_insurance_payments = InsuranceService.get_pending_insurances()
    expiring_auths = AuthorizationService.get_expiring_soon(30)
    stats = {
        'expired_itvs_count': len(expired_itvs),
        'expiring_itvs_count': len(expiring_itvs),
        'pending_taxes_count': len(pending_taxes),
        'overdue_taxes_count': len(overdue_taxes),
        'pending_fines_count': len(pending_fines),
        'overdue_fines_count': len(overdue_fines),
        'expiring_insurances_count': len(expiring_insurances),
        'expired_insurances_count': len(expired_insurances),
        'pending_insurance_payments_count': len(pending_insurance_payments),
        'expiring_auths_count': len(expiring_auths),
        'total_pending_fines_amount': sum(f.amount for f in pending_fines),
        'total_pending_taxes_amount': sum(float(t.amount) for t in pending_taxes)
    }
    
    return render_template('compliance/dashboard.html', 
                         stats=stats,
                         expired_itvs=expired_itvs[:5],
                         pending_fines=pending_fines[:5])
@login_required
def insurance_list():
    """Insurance records list"""
    insurances = InsuranceService.get_all_insurances()
    return render_template('compliance/insurances.html', insurances=insurances)

# ============= ITV Routes =============
@compliance_bp.route('/itv')
@login_required
def itv_records():
    """ITV records list"""
    records = ITVService.get_all_itv_records()
    return render_template('compliance/itv.html', records=records)

@compliance_bp.route('/itv/<int:record_id>')
@login_required
def view_itv(record_id):
    """View ITV record details"""
    record = ITVService.get_itv_by_id(record_id)
    if not record:
        flash('Registro de ITV no encontrado', 'error')
        return redirect(url_for('compliance.itv_records'))
    return render_template('compliance/itv_detail.html', record=record)

@compliance_bp.route('/itv/new', methods=['GET', 'POST'])
@login_required
def create_itv():
    """Create new ITV record"""
    if request.method == 'POST':
        try:
            insp_str = request.form.get('inspection_date')
            exp_str = request.form.get('expiry_date')
            if not insp_str:
                raise ValueError('Debe proporcionar la fecha de inspección')
            if not exp_str:
                raise ValueError('Debe proporcionar la fecha de caducidad')
            try:
                inspection_date = datetime.strptime(insp_str, '%Y-%m-%d')
                expiry_date = datetime.strptime(exp_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido, use YYYY-MM-DD')
            
            record = ITVService.create_itv(
                vehicle_id=int(request.form.get('vehicle_id')),
                inspection_date=inspection_date,
                expiry_date=expiry_date,
                result=ITVResult(request.form.get('result')),
                inspection_center=request.form.get('inspection_center'),
                certificate_number=request.form.get('certificate_number'),
                cost=parse_money(request.form.get('cost')) if request.form.get('cost') else None,
                mileage_at_inspection=int(request.form.get('mileage_at_inspection')) if request.form.get('mileage_at_inspection') else None,
                defects_found=request.form.get('defects_found'),
                notes=request.form.get('notes')
            )
            flash('Registro de ITV creado exitosamente', 'success')
            return redirect(url_for('compliance.view_itv', record_id=record.id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear registro (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/itv_form.html', vehicles=vehicles, itv_results=ITVResult)

# ============= Tax Routes =============
@compliance_bp.route('/taxes')
@login_required
def tax_records():
    """Tax records list"""
    records = TaxService.get_all_taxes()
    return render_template('compliance/taxes.html', records=records)

@compliance_bp.route('/taxes/<int:tax_id>')
@login_required
def view_tax(tax_id):
    """View tax record details"""
    record = TaxService.get_tax_by_id(tax_id)
    if not record:
        flash('Registro de impuesto no encontrado', 'error')
        return redirect(url_for('compliance.tax_records'))
    return render_template('compliance/tax_detail.html', record=record)

@compliance_bp.route('/taxes/new', methods=['GET', 'POST'])
@login_required
def create_tax():
    """Create new tax record"""
    if request.method == 'POST':
        try:
            due_str = request.form.get('due_date')
            if not due_str:
                raise ValueError('Debe proporcionar la fecha de vencimiento')
            try:
                due_date = datetime.strptime(due_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido, use YYYY-MM-DD')
            
            record = TaxService.create_tax(
                vehicle_id=int(request.form.get('vehicle_id')),
                tax_type=TaxType(request.form.get('tax_type')),
                tax_year=int(request.form.get('tax_year')),
                amount=parse_money(request.form.get('amount')),
                due_date=due_date,
                notes=request.form.get('notes')
            )
            flash('Registro de impuesto creado exitosamente', 'success')
            return redirect(url_for('compliance.view_tax', tax_id=record.id))
        except Exception as e:
            from app.utils.error_helpers import log_exception
            err_id = log_exception(e, __name__)
            flash(f'Error al crear registro (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/tax_form.html', vehicles=vehicles, tax_types=TaxType)

@compliance_bp.route('/taxes/<int:tax_id>/pay', methods=['POST'])
@login_required
def pay_tax(tax_id):
    """Mark tax as paid"""
    try:
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d')
        TaxService.mark_as_paid(
            tax_id,
            payment_date,
            request.form.get('payment_method'),
            request.form.get('payment_reference')
        )
        flash('Impuesto marcado como pagado', 'success')
    except Exception as e:
        from app.utils.error_helpers import log_exception
        err_id = log_exception(e, __name__)
        flash(f'Error: (id={err_id})', 'error')
    return redirect(url_for('compliance.view_tax', tax_id=tax_id))

# ============= Insurance Routes =============
@compliance_bp.route('/insurances')
@login_required
def insurance_list():
    """Insurance records list"""
    insurances = InsuranceService.get_all_insurances()
    return render_template('compliance/insurances.html', insurances=insurances)

@compliance_bp.route('/insurances/<int:insurance_id>')
@login_required
def view_insurance(insurance_id):
    """View insurance record details"""
    record = InsuranceService.get_insurance_by_id(insurance_id)
    if not record:
        flash('Registro de seguro no encontrado', 'error')
        return redirect(url_for('compliance.insurance_list'))
    return render_template('compliance/insurance_detail.html', record=record)

@compliance_bp.route('/insurances/new', methods=['GET', 'POST'])
@login_required
def create_insurance():
    """Create new insurance record"""
    if request.method == 'POST':
        try:
            start_str = request.form.get('start_date')
            end_str = request.form.get('end_date')
            if not start_str:
                raise ValueError('Debe proporcionar la fecha de inicio')
            if not end_str:
                raise ValueError('Debe proporcionar la fecha de fin')
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido, use YYYY-MM-DD')
            # Handle file upload using helper and app config
            document = request.files.get('document')
            document_path = None
            if document and document.filename:
                upload_dir = current_app.config.get('INSURANCE_UPLOAD_FOLDER')
                allowed_ext = current_app.config.get('INSURANCE_ALLOWED_EXTENSIONS')
                max_bytes = current_app.config.get('INSURANCE_MAX_BYTES')
                try:
                    document_path, _ = save_uploaded_file(document, upload_dir, allowed_ext, max_bytes)
                except UploadError as ue:
                    err_id = uuid.uuid4().hex[:8]
                    logging.getLogger(__name__).exception('Upload failed [%s]: %s', err_id, ue)
                    flash(f'Error al subir fichero (id={err_id}). {str(ue)}', 'error')
                    return redirect(url_for('compliance.create_insurance'))

            record = InsuranceService.create_insurance(
                vehicle_id=int(request.form.get('vehicle_id')),
                insurance_type=InsuranceType(request.form.get('insurance_type')),
                insurance_company=request.form.get('insurance_company'),
                policy_number=request.form.get('policy_number'),
                premium_amount=parse_money(request.form.get('premium_amount')),
                start_date=start_date,
                end_date=end_date,
                coverage_details=request.form.get('coverage_details'),
                notes=request.form.get('notes'),
                document_path=document_path
            )
            flash('Registro de seguro creado exitosamente', 'success')
            return redirect(url_for('compliance.view_insurance', insurance_id=record.id))
        except ValueError as ve:
            # parse_money may raise ValueError for invalid formats
            err_id = log_exception(ve, __name__)
            flash(f'Entrada inválida: {str(ve)} (id={err_id})', 'error')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al crear registro (id={err_id})', 'error')

    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/insurance_form.html', vehicles=vehicles, insurance_types=InsuranceType)

@compliance_bp.route('/insurances/<int:insurance_id>/pay', methods=['POST'])
@login_required
def pay_insurance(insurance_id):
    """Mark insurance as paid"""
    try:
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d')
        InsuranceService.mark_as_paid(
            insurance_id,
            payment_date,
            request.form.get('payment_method'),
            request.form.get('payment_reference')
        )
        flash('Seguro marcado como pagado', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error: (id={err_id})', 'error')
    return redirect(url_for('compliance.view_insurance', insurance_id=insurance_id))

@compliance_bp.route('/insurances/<int:insurance_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_insurance(insurance_id):
    """Edit insurance record"""
    record = InsuranceService.get_insurance_by_id(insurance_id)
    if not record:
        flash('Registro de seguro no encontrado', 'error')
        return redirect(url_for('compliance.insurance_list'))

    if request.method == 'POST':
        try:
            start_str = request.form.get('start_date')
            end_str = request.form.get('end_date')
            if not start_str:
                raise ValueError('Debe proporcionar la fecha de inicio')
            if not end_str:
                raise ValueError('Debe proporcionar la fecha de fin')
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido, use YYYY-MM-DD')

            # Handle optional file upload via helper
            document = request.files.get('document')
            document_path = None
            if document and document.filename:
                upload_dir = current_app.config.get('INSURANCE_UPLOAD_FOLDER')
                allowed_ext = current_app.config.get('INSURANCE_ALLOWED_EXTENSIONS')
                max_bytes = current_app.config.get('INSURANCE_MAX_BYTES')
                try:
                    document_path, _ = save_uploaded_file(document, upload_dir, allowed_ext, max_bytes)
                except UploadError as ue:
                    err_id = uuid.uuid4().hex[:8]
                    logging.getLogger(__name__).exception('Upload failed [%s]: %s', err_id, ue)
                    flash(f'Error al subir fichero (id={err_id}). {str(ue)}', 'error')
                    return redirect(url_for('compliance.edit_insurance', insurance_id=insurance_id))

            update_kwargs = dict(
                insurance_type=InsuranceType(request.form.get('insurance_type')),
                insurance_company=request.form.get('insurance_company'),
                policy_number=request.form.get('policy_number'),
                premium_amount=parse_money(request.form.get('premium_amount')),
                start_date=start_date,
                end_date=end_date,
                coverage_details=request.form.get('coverage_details'),
                notes=request.form.get('notes')
            )
            if document_path:
                update_kwargs['document_path'] = document_path

            InsuranceService.update_insurance(insurance_id, **update_kwargs)
            flash('Registro de seguro actualizado exitosamente', 'success')
            return redirect(url_for('compliance.view_insurance', insurance_id=insurance_id))
        except ValueError as ve:
            err_id = log_exception(ve, __name__)
            flash(f'Entrada inválida: {str(ve)} (id={err_id})', 'error')
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar registro (id={err_id})', 'error')

    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/insurance_form.html', record=record, vehicles=vehicles, insurance_types=InsuranceType)

@compliance_bp.route('/insurances/<int:insurance_id>/delete', methods=['POST'])
@login_required
def delete_insurance(insurance_id):
    """Delete insurance record"""
    try:
        InsuranceService.delete_insurance(insurance_id)
        flash('Registro de seguro eliminado exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar registro (id={err_id})', 'error')
    return redirect(url_for('compliance.insurance_list'))

# ============= Fine Routes =============
@compliance_bp.route('/fines')
@login_required
def fine_records():
    """Fine records list"""
    records = FineService.get_all_fines()
    return render_template('compliance/fines.html', records=records)

@compliance_bp.route('/fines/<int:fine_id>')
@login_required
def view_fine(fine_id):
    """View fine details"""
    record = FineService.get_fine_by_id(fine_id)
    if not record:
        flash('Multa no encontrada', 'error')
        return redirect(url_for('compliance.fine_records'))
    return render_template('compliance/fine_detail.html', record=record)

@compliance_bp.route('/fines/new', methods=['GET', 'POST'])
@login_required
def create_fine():
    """Create new fine"""
    if request.method == 'POST':
        try:
            fine_str = request.form.get('fine_date')
            if not fine_str:
                raise ValueError('Debe proporcionar la fecha de la multa')
            try:
                fine_date = datetime.strptime(fine_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido, use YYYY-MM-DD')
            payment_deadline = datetime.strptime(request.form.get('payment_deadline'), '%Y-%m-%d') if request.form.get('payment_deadline') else None
            
            record = FineService.create_fine(
                vehicle_id=int(request.form.get('vehicle_id')),
                fine_number=request.form.get('fine_number'),
                fine_type=FineType(request.form.get('fine_type')),
                fine_date=fine_date,
                description=request.form.get('description'),
                amount=parse_money(request.form.get('amount')),
                payment_deadline=payment_deadline,
                location=request.form.get('location'),
                driver_id=int(request.form.get('driver_id')) if request.form.get('driver_id') else None,
                notes=request.form.get('notes')
            )
            flash('Multa registrada exitosamente', 'success')
            return redirect(url_for('compliance.view_fine', fine_id=record.id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al registrar multa (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/fine_form.html', vehicles=vehicles, fine_types=FineType)

@compliance_bp.route('/fines/<int:fine_id>/pay', methods=['POST'])
@login_required
def pay_fine(fine_id):
    """Mark fine as paid"""
    try:
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d')
        payment_amount = parse_money(request.form.get('payment_amount'))
        FineService.mark_as_paid(fine_id, payment_date, payment_amount)
        flash('Multa marcada como pagada', 'success')
    except Exception as e:
        from app.utils.error_helpers import log_exception
        err_id = log_exception(e, __name__)
        flash(f'Error: (id={err_id})', 'error')
    return redirect(url_for('compliance.view_fine', fine_id=fine_id))

# ============= Authorization Routes =============
@compliance_bp.route('/authorizations')
@login_required
def authorization_records():
    """Authorization records list"""
    records = AuthorizationService.get_all_authorizations()
    return render_template('compliance/authorizations.html', records=records)

@compliance_bp.route('/authorizations/<int:auth_id>')
@login_required
def view_authorization(auth_id):
    """View authorization details"""
    record = AuthorizationService.get_authorization_by_id(auth_id)
    if not record:
        flash('Autorización no encontrada', 'error')
        return redirect(url_for('compliance.authorization_records'))
    return render_template('compliance/authorization_detail.html', record=record)

@compliance_bp.route('/authorizations/new', methods=['GET', 'POST'])
@login_required
def create_authorization():
    """Create new authorization"""
    if request.method == 'POST':
        try:
            start_str = request.form.get('start_date')
            end_str = request.form.get('end_date')
            if not start_str:
                raise ValueError('Debe proporcionar la fecha de inicio')
            if not end_str:
                raise ValueError('Debe proporcionar la fecha de fin')
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Formato de fecha inválido, use YYYY-MM-DD')
            
            record = AuthorizationService.create_authorization(
                vehicle_id=int(request.form.get('vehicle_id')),
                authorization_type=request.form.get('authorization_type'),
                issuing_authority=request.form.get('issuing_authority'),
                authorization_number=request.form.get('authorization_number'),
                start_date=start_date,
                end_date=end_date,
                zone_description=request.form.get('zone_description'),
                conditions=request.form.get('conditions'),
                notes=request.form.get('notes')
            )
            flash('Autorización creada exitosamente', 'success')
            return redirect(url_for('compliance.view_authorization', auth_id=record.id))
        except Exception as e:
            from app.utils.error_helpers import log_exception
            err_id = log_exception(e, __name__)
            flash(f'Error al crear autorización (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/authorization_form.html', vehicles=vehicles)

@compliance_bp.route('/itv/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_itv(record_id):
    """Edit ITV record"""
    record = ITVService.get_itv_by_id(record_id)
    if not record:
        flash('Registro de ITV no encontrado', 'error')
        return redirect(url_for('compliance.itv_records'))
    
    if request.method == 'POST':
        try:
            inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d')
            expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d')
            
            ITVService.update_itv(
                record_id,
                inspection_date=inspection_date,
                expiry_date=expiry_date,
                result=ITVResult(request.form.get('result')),
                inspection_center=request.form.get('inspection_center'),
                certificate_number=request.form.get('certificate_number'),
                cost=parse_money(request.form.get('cost')) if request.form.get('cost') else None,
                mileage_at_inspection=int(request.form.get('mileage_at_inspection')) if request.form.get('mileage_at_inspection') else None,
                defects_found=request.form.get('defects_found'),
                notes=request.form.get('notes')
            )
            flash('Registro de ITV actualizado exitosamente', 'success')
            return redirect(url_for('compliance.view_itv', record_id=record_id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar registro: (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/itv_form.html', record=record, vehicles=vehicles, itv_results=ITVResult)

@compliance_bp.route('/itv/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_itv(record_id):
    """Delete ITV record"""
    try:
        ITVService.delete_itv(record_id)
        flash('Registro de ITV eliminado exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar registro: (id={err_id})', 'error')
    return redirect(url_for('compliance.itv_records'))

@compliance_bp.route('/taxes/<int:tax_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tax(tax_id):
    """Edit tax record"""
    record = TaxService.get_tax_by_id(tax_id)
    if not record:
        flash('Registro de impuesto no encontrado', 'error')
        return redirect(url_for('compliance.tax_records'))
    
    if request.method == 'POST':
        try:
            due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
            
            TaxService.update_tax(
                tax_id,
                tax_type=TaxType(request.form.get('tax_type')),
                tax_year=int(request.form.get('tax_year')),
                amount=parse_money(request.form.get('amount')),
                due_date=due_date,
                notes=request.form.get('notes')
            )
            flash('Registro de impuesto actualizado exitosamente', 'success')
            return redirect(url_for('compliance.view_tax', tax_id=tax_id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar registro: (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/tax_form.html', record=record, vehicles=vehicles, tax_types=TaxType)

@compliance_bp.route('/taxes/<int:tax_id>/delete', methods=['POST'])
@login_required
def delete_tax(tax_id):
    """Delete tax record"""
    try:
        TaxService.delete_tax(tax_id)
        flash('Registro de impuesto eliminado exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar registro: (id={err_id})', 'error')
    return redirect(url_for('compliance.tax_records'))

@compliance_bp.route('/fines/<int:fine_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_fine(fine_id):
    """Edit fine record"""
    record = FineService.get_fine_by_id(fine_id)
    if not record:
        flash('Multa no encontrada', 'error')
        return redirect(url_for('compliance.fine_records'))
    
    if request.method == 'POST':
        try:
            fine_date = datetime.strptime(request.form.get('fine_date'), '%Y-%m-%d')
            payment_deadline = datetime.strptime(request.form.get('payment_deadline'), '%Y-%m-%d') if request.form.get('payment_deadline') else None

            FineService.update_fine(
                fine_id,
                fine_type=FineType(request.form.get('fine_type')),
                fine_date=fine_date,
                description=request.form.get('description'),
                amount=parse_money(request.form.get('amount')),
                payment_deadline=payment_deadline,
                location=request.form.get('location'),
                notes=request.form.get('notes')
            )
            flash('Multa actualizada exitosamente', 'success')
            return redirect(url_for('compliance.view_fine', fine_id=fine_id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar multa: (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/fine_form.html', record=record, vehicles=vehicles, fine_types=FineType)

@compliance_bp.route('/fines/<int:fine_id>/delete', methods=['POST'])
@login_required
def delete_fine(fine_id):
    """Delete fine record"""
    try:
        FineService.delete_fine(fine_id)
        flash('Multa eliminada exitosamente', 'success')
    except Exception as e:
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar multa: (id={err_id})', 'error')
    return redirect(url_for('compliance.fine_records'))

@compliance_bp.route('/authorizations/<int:auth_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_authorization(auth_id):
    """Edit authorization record"""
    record = AuthorizationService.get_authorization_by_id(auth_id)
    if not record:
        flash('Autorización no encontrada', 'error')
        return redirect(url_for('compliance.authorization_records'))
    
    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
            
            AuthorizationService.update_authorization(
                auth_id,
                authorization_type=request.form.get('authorization_type'),
                issuing_authority=request.form.get('issuing_authority'),
                authorization_number=request.form.get('authorization_number'),
                start_date=start_date,
                end_date=end_date,
                zone_description=request.form.get('zone_description'),
                conditions=request.form.get('conditions'),
                notes=request.form.get('notes')
            )
            flash('Autorización actualizada exitosamente', 'success')
            return redirect(url_for('compliance.view_authorization', auth_id=auth_id))
        except Exception as e:
            err_id = log_exception(e, __name__)
            flash(f'Error al actualizar autorización: (id={err_id})', 'error')
    
    vehicles = VehicleService.get_all_vehicles()
    return render_template('compliance/authorization_form.html', record=record, vehicles=vehicles)

@compliance_bp.route('/authorizations/<int:auth_id>/delete', methods=['POST'])
@login_required
def delete_authorization(auth_id):
    """Delete authorization record"""
    try:
        AuthorizationService.delete_authorization(auth_id)
        flash('Autorización eliminada exitosamente', 'success')
    except Exception as e:
        from app.utils.error_helpers import log_exception
        err_id = log_exception(e, __name__)
        flash(f'Error al eliminar autorización (id={err_id})', 'error')
    return redirect(url_for('compliance.authorization_records'))
