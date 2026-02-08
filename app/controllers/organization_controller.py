"""Organization controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.organization_service import OrganizationService
from app.models.organization import OrganizationUnit
from app.utils.error_helpers import log_exception
from app.services.provider_service import ProviderService
from app.services.vehicle_service import VehicleService
from app.services.vehicle_assignment_service import VehicleAssignmentService
from app.services.itv_service import ITVService
from app.services.insurance_service import InsuranceService
from app.services.tax_service import TaxService
from app.models.vehicle_driver_association import VehicleDriverAssociation
from app.models.user import UserRole
from app.core.permissions import has_role

organization_bp = Blueprint('organizations', __name__)

def build_organization_tree(organizations):
    """Build hierarchical tree structure from flat organization list"""
    org_dict = {org.id: org for org in organizations}
    tree = []

    for org in organizations:
        if org.parent_id is None:
            # Root level organization
            tree.append(org)
        else:
            # Child organization - add to parent's children
            parent = org_dict.get(org.parent_id)
            if parent:
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(org)

    return tree

def build_organization_tree_from_relationships():
    """Build tree using SQLAlchemy relationships with efficient querying"""
    from sqlalchemy.orm import joinedload
    
    # Load all organizations with their relationships in a single query
    all_orgs = OrganizationUnit.query.filter_by(is_active=True).options(
        joinedload(OrganizationUnit.parent)
    ).order_by(OrganizationUnit.parent_id, OrganizationUnit.name).all()
    
    # Create a dictionary to store nodes by their ID
    org_dict = {org.id: org for org in all_orgs}
    
    # Build the tree structure
    root_orgs = []
    
    for org in all_orgs:
        if not hasattr(org, 'children'):
            org.children = []
            
        if org.parent_id is None:
            root_orgs.append(org)
        else:
            parent = org_dict.get(org.parent_id)
            if parent:
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(org)
    
    return root_orgs

def serialize_org_for_tree(org):
    """Convert OrganizationUnit to a serializable dict for jsTree"""
    if not org:
        return None
        
    try:
        # Create the base node
        node = {
            'id': f'org_{org.id}',
            'text': f"{org.name} ({org.code if org.code else 'Sin código'})",
            'parent': f'org_{org.parent_id}' if org.parent_id else '#',
            'data': {
                'type': getattr(org, 'type', 'organization').lower(),
                'email': getattr(org, 'contact_email', 'No especificado'),
                'phone': getattr(org, 'contact_phone', 'No especificado'),
                'code': getattr(org, 'code', ''),
                'name': getattr(org, 'name', 'Sin nombre'),
                'is_active': getattr(org, 'is_active', True)
            }
        }
        
        # Recursively process children if they exist
        if hasattr(org, 'children') and org.children:
            node['children'] = [serialize_org_for_tree(child) for child in org.children]
            
        return node
        
    except Exception as e:
        print(f"Error serializing organization {getattr(org, 'id', 'unknown')}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
    try:
        # Safely get attributes with defaults
        org_id = getattr(org, 'id', '')
        name = get_safe_value(getattr(org, 'name', 'Sin nombre'))
        code = get_safe_value(getattr(org, 'code', ''))
        contact_email = get_safe_value(getattr(org, 'contact_email', 'No especificado'))
        contact_phone = get_safe_value(getattr(org, 'contact_phone', 'No especificado'))
        parent_id = get_safe_value(getattr(org, 'parent_id', None))
        
        # Ensure all values are JSON serializable
        node = {
            'id': f'org_{org_id}',
            'text': f"{name} ({code if code else 'Sin código'})",
            'data': {
                'org_id': str(org_id) if org_id is not None else '',
                'code': str(code) if code is not None else '',
                'email': str(contact_email) if contact_email is not None else '',
                'phone': str(contact_phone) if contact_phone is not None else '',
                'parent_id': str(parent_id) if parent_id is not None else None
            },
            'state': {
                'opened': True,
                'disabled': False,
                'selected': False
            },
            'icon': 'bi bi-diagram-3',
            'children': bool(getattr(org, 'children', [])),
            'children_d': [serialize_org_for_tree(c) for c in getattr(org, 'children', [])]
        }
        
        # Ensure all values in the node are JSON serializable
        import json
        json.dumps(node)  # This will raise an error if anything is not serializable
        
        return node
        
    except Exception as e:
        print(f"Error serializing organization: {str(e)}")
        # Return a minimal valid node with error information
        return {
            'id': 'error_node',
            'text': 'Error loading organization',
            'data': {},
            'state': {'opened': True, 'disabled': True, 'selected': False},
            'icon': 'bi bi-exclamation-triangle',
            'children': False,
            'children_d': []
        }

def _load_children(org):
    """Recursively load children for an organization"""
    children = OrganizationUnit.query.filter_by(parent_id=org.id, is_active=True).all()
    org.children = children

    for child in children:
        _load_children(child)

@organization_bp.route('/')
@login_required
@has_role(UserRole.ADMIN)
def list_organizations():
    """List all organizations"""
    organizations = OrganizationService.get_all_organizations()
    # Build hierarchical tree using relationships
    org_tree_objs = build_organization_tree_from_relationships()
    # Create a flat list of organizations in the required format
    org_tree = []
    for org in organizations:
        org_node = {
            'id': f'org_{org.id}',
            'parent': f'org_{org.parent_id}' if org.parent_id else '#',
            'text': org.name  # Only show name, no code
        }
        org_tree.append(org_node)
    
    # Convert to JSON string
    import json
    org_tree_json = json.dumps(org_tree, ensure_ascii=False)
    
    return render_template('organizations/tree.html', 
                         org_tree=org_tree,
                         org_tree_json=org_tree_json,
                         organizations=organizations)


@organization_bp.route('/tree')
@login_required
@has_role(UserRole.ADMIN)
def tree_organizations():
    """Render organizations as a hierarchical tree using jsTree"""
    try:
        # Get all organizations
        organizations = OrganizationService.get_all_organizations()
        
        # Create a flat list of organizations with all properties
        org_tree = []
        for org in organizations:
            org_node = {
                'id': f'org_{org.id}',
                'parent': f'org_{org.parent_id}' if org.parent_id else '#',
                'text': f"{org.name} ({org.code})" if org.code else org.name,
                'data': {
                    'name': org.name,
                    'code': org.code,
                    'description': org.description,
                    'email': org.email,
                    'phone': org.phone,
                    'is_active': org.is_active,
                    'created_at': org.created_at.isoformat() if org.created_at else None,
                    'updated_at': org.updated_at.isoformat() if org.updated_at else None
                },
                'icon': 'bi bi-diagram-3',
                'state': {
                    'opened': True,
                    'disabled': not org.is_active
                }
            }
            # Only add if it's not a duplicate
            if not any(node['id'] == org_node['id'] for node in org_tree):
                org_tree.append(org_node)
        
        # Sort to ensure parents come before children
        org_tree.sort(key=lambda x: (x['parent'] == '#', x['parent'], x['id']))
        
        # Convert to JSON string with proper date serialization
        import json
        from datetime import datetime
        
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
            
        org_tree_json = json.dumps(org_tree, default=json_serial, ensure_ascii=False)
        
        return render_template('organizations/tree.html',
                            org_tree=org_tree,
                            org_tree_json=org_tree_json,
                            organizations=organizations)
                            
    except Exception as e:
        print(f"Critical error in tree_organizations: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty tree if there's an error
        return render_template('organizations/tree.html', 
                            org_tree=[],
                            org_tree_json='[]')  # Empty JSON array as string


@organization_bp.route('/tree.json')
@login_required
@has_role(UserRole.ADMIN)
def tree_organizations_json():
    """Return organization tree as JSON (serializable structure for jsTree)"""
    try:
        current_app.logger.info("Building organization tree...")
        
        # Get all organizations and build the tree structure
        org_tree_objs = build_organization_tree_from_relationships()
        current_app.logger.info(f"Found {len(org_tree_objs)} root organizations")
        
        # Serialize the tree structure
        serialized = []
        for org in org_tree_objs:
            node = serialize_org_for_tree(org)
            if node:  # Only add if serialization was successful
                serialized.append(node)
        
        # Flatten the tree structure for jsTree
        def flatten_tree(nodes):
            result = []
            for node in nodes:
                if not node:
                    continue
                # Create a copy of the node without children
                flat_node = node.copy()
                if 'children' in flat_node:
                    # Add children to the result and update parent references
                    children = flat_node.pop('children', [])
                    result.extend(flatten_tree(children))
                result.append(flat_node)
            return result
        
        flat_tree = flatten_tree(serialized)
        
        # Create response
        response_data = {
            "status": "success",
            "data": flat_tree,
            "count": len(flat_tree)
        }
        
        response = make_response(jsonify(flat_tree))  # Return just the array for jsTree
        response.headers['Content-Type'] = 'application/json'
        
        current_app.logger.info(f"Successfully serialized {len(flat_tree)} organization nodes")
        return response
        
    except Exception as e:
        error_msg = f"Error generating organization tree: {str(e)}\n{traceback.format_exc()}"
        current_app.logger.error(error_msg)
        
        response = make_response(jsonify({
            "status": "error",
            "message": "Error al cargar el árbol de organizaciones",
            "error": str(e)
        }), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

@organization_bp.route('/<int:org_id>')
@login_required
def view_organization(org_id):
    """View organization details"""
    org = OrganizationService.get_organization_by_id(org_id)
    if not org:
        flash('Organización no encontrada', 'error')
        return redirect(url_for('organizations.list_organizations'))
    return render_template('organizations/detail.html', organization=org)


@organization_bp.route('/<int:org_id>/dashboard')
@login_required
@has_role(UserRole.ADMIN, UserRole.FLEET_MANAGER, UserRole.OPERATIONS_MANAGER)
def organization_dashboard(org_id):
    """Dashboard view scoped to a single organization unit"""
    org = OrganizationService.get_organization_by_id(org_id)
    if not org:
        flash('Organización no encontrada', 'error')
        return redirect(url_for('organizations.list_organizations'))

    # Vehicles assigned to this organization
    vehicles = VehicleService.get_all_vehicles(organization_unit_id=org_id)

    # Providers for this organization
    providers = ProviderService.get_all_providers(organization_unit_id=org_id)

    # Active driver assignments for vehicles in this org (join VehicleDriverAssociation -> Vehicle)
    active_assignments = VehicleDriverAssociation.query.join(VehicleDriverAssociation.vehicle).filter(
        VehicleDriverAssociation.is_active == True,
        VehicleDriverAssociation.vehicle.has(organization_unit_id=org_id)
    ).all()

    # Cesiones / vehicle assignment records linked to this organization (organization_unit_id on VehicleAssignment)
    all_cesiones = VehicleAssignmentService.get_all_assignments()
    cesiones = [c for c in all_cesiones if c.organization_unit_id == org_id]

    # Compliance: aggregate basic compliance status per vehicle
    compliance = []
    for v in vehicles:
        latest_itv = ITVService.get_latest_itv(v.id)
        latest_insurance = InsuranceService.get_latest_insurance(v.id) if hasattr(InsuranceService, 'get_latest_insurance') else None
        pending_taxes = TaxService.get_taxes_by_vehicle(v.id) if hasattr(TaxService, 'get_taxes_by_vehicle') else []
        compliance.append({
            'vehicle': v,
            'itv': latest_itv,
            'insurance': latest_insurance,
            'pending_taxes': pending_taxes
        })

    # Simple stats
    stats = {
        'total_vehicles': len(vehicles),
        'total_providers': len(providers),
        'active_assignments': len(active_assignments),
        'cesiones': len(cesiones)
    }

    return render_template('organizations/dashboard.html',
                         organization=org,
                         vehicles=vehicles,
                         providers=providers,
                         active_assignments=active_assignments,
                         cesiones=cesiones,
                         compliance=compliance,
                         stats=stats)

def get_organizations_with_levels(organizations, parent_id=None, level=0):
    """Get organizations with hierarchy levels for select dropdown"""
    result = []
    for org in organizations:
        if org.parent_id == parent_id:
            org.level = level
            result.append(org)
            # Add children with increased level
            result.extend(get_organizations_with_levels(
                [o for o in organizations if o.id != org.id], 
                org.id, 
                level + 1
            ))
    return result

@organization_bp.route('/new', methods=['GET', 'POST'])
@login_required
@has_role(UserRole.ADMIN)
def create_organization():
    """Create new organization"""
    if request.method == 'POST':
        try:
            data = request.form
            parent_id = data.get('parent_id')
            if parent_id == '':
                parent_id = None
            
            organization = OrganizationService.create_organization(
                name=data['name'],
                code=data['code'],
                description=data.get('description'),
                manager_name=data.get('manager_name'),
                contact_email=data.get('contact_email'),
                contact_phone=data.get('contact_phone'),
                parent_id=parent_id
            )
            flash('Organización creada exitosamente', 'success')
            return redirect(url_for('organizations.view_organization', org_id=organization.id))
        except Exception as e:
            log_exception(f'Error creating organization: {str(e)}')
            flash('Error al crear la organización', 'error')
    
    all_orgs = OrganizationService.get_all_organizations()
    organizations = get_organizations_with_levels(all_orgs)
    return render_template('organizations/form_with_select.html', 
                         organization=None, 
                         organizations=organizations)

@organization_bp.route('/<int:org_id>/edit', methods=['GET', 'POST'])
@login_required
@has_role(UserRole.ADMIN)
def edit_organization(org_id):
    """Edit organization"""
    organization = OrganizationService.get_organization_by_id(org_id)
    if not organization:
        flash('Organización no encontrada', 'error')
        return redirect(url_for('organizations.list_organizations'))
    
    if request.method == 'POST':
        try:
            data = request.form
            parent_id = data.get('parent_id')
            if parent_id == '':
                parent_id = None
            
            organization = OrganizationService.update_organization(
                org_id=org_id,
                name=data['name'],
                code=data['code'],
                description=data.get('description'),
                manager_name=data.get('manager_name'),
                contact_email=data.get('contact_email'),
                contact_phone=data.get('contact_phone'),
                parent_id=parent_id
            )
            flash('Organización actualizada exitosamente', 'success')
            return redirect(url_for('organizations.view_organization', org_id=org_id))
        except Exception as e:
            log_exception(f'Error updating organization: {str(e)}')
            flash('Error al actualizar la organización', 'error')
    
    # Get all organizations except current one and add hierarchy levels
    all_orgs = [o for o in OrganizationService.get_all_organizations() if o.id != org_id]
    organizations = get_organizations_with_levels(all_orgs)
    
    return render_template('organizations/form_with_select.html', 
                         organization=organization, 
                         organizations=organizations)

@organization_bp.route('/<int:org_id>/delete', methods=['POST'])
@login_required
@has_role(UserRole.ADMIN)
def delete_organization(org_id):
    """Delete organization"""
    if OrganizationService.delete_organization(org_id):
        flash('Organización eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar organización', 'error')
    return redirect(url_for('organizations.list_organizations'))
