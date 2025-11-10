"""Pickup controller"""
from flask import Blueprint, render_template, request, url_for
from flask_login import login_required
from urllib.parse import urlencode
from app.utils.pagination import paginate_list

pickup_bp = Blueprint('pickups', __name__)


@pickup_bp.route('/')
@login_required
def list_pickups():
    """List all pickups"""
    # defensive pagination for consistency with other list endpoints
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        per_page = 20

    preserved_args = {k: v for k, v in request.args.items() if k != 'page'}
    base_list_url = url_for('pickups.list_pickups')
    preserved_qs = urlencode(preserved_args) if preserved_args else ''

    # currently no pickups stored; keep compatibility by returning an empty pagination
    all_pickups = []
    pickups, pagination = paginate_list(all_pickups, page=page, per_page=per_page)

    return render_template('pickups/list.html', pickups=pickups, pagination=pagination, base_list_url=base_list_url, preserved_qs=preserved_qs)

@pickup_bp.route('/<int:pickup_id>')
@login_required
def view_pickup(pickup_id):
    """View pickup details"""
    return render_template('pickups/detail.html', pickup_id=pickup_id)
