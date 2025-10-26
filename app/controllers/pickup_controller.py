"""Pickup controller"""
from flask import Blueprint, render_template
from flask_login import login_required

pickup_bp = Blueprint('pickups', __name__)

@pickup_bp.route('/')
@login_required
def list_pickups():
    """List all pickups"""
    return render_template('pickups/list.html', pickups=[])

@pickup_bp.route('/<int:pickup_id>')
@login_required
def view_pickup(pickup_id):
    """View pickup details"""
    return render_template('pickups/detail.html', pickup_id=pickup_id)
