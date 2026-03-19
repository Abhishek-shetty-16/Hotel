from flask import Blueprint, request, jsonify
from models.models import MenuItem, Category, AdminUser, Order
from extensions import db
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)


# ─── Category Management ────────────────────────────────────────────────────

@admin_bp.route('/categories', methods=['GET'])
def get_categories():
    cats = Category.query.all()
    return jsonify([c.to_dict() for c in cats])


@admin_bp.route('/categories', methods=['POST'])
def add_category():
    data = request.get_json()
    cat = Category(category_name=data['category_name'])
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@admin_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    data = request.get_json()
    cat.category_name = data.get('category_name', cat.category_name)
    db.session.commit()
    return jsonify(cat.to_dict())


@admin_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'message': 'Category deleted'})


# ─── Menu Item Management ───────────────────────────────────────────────────

@admin_bp.route('/menu', methods=['GET'])
def get_all_menu():
    items = MenuItem.query.all()
    return jsonify([i.to_dict() for i in items])


@admin_bp.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    item = MenuItem(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        category_id=data.get('category_id'),
        image_url=data.get('image_url'),
        is_available=data.get('is_available', True)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@admin_bp.route('/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.price = data.get('price', item.price)
    item.category_id = data.get('category_id', item.category_id)
    item.image_url = data.get('image_url', item.image_url)
    item.is_available = data.get('is_available', item.is_available)
    db.session.commit()
    return jsonify(item.to_dict())


@admin_bp.route('/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'})


@admin_bp.route('/menu/<int:item_id>/toggle', methods=['PUT'])
def toggle_availability(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.is_available = not item.is_available
    db.session.commit()
    return jsonify({'message': 'Availability toggled', 'is_available': item.is_available})


# ─── Order Management ───────────────────────────────────────────────────────

@admin_bp.route('/orders', methods=['GET'])
def get_all_orders():
    status = request.args.get('status')
    query = Order.query.order_by(Order.created_at.desc())
    if status:
        query = query.filter_by(order_status=status)
    orders = query.all()
    return jsonify([o.to_dict() for o in orders])


@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    VALID = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
    data = request.get_json()
    new_status = data.get('order_status')
    if new_status not in VALID:
        return jsonify({'error': 'Invalid status'}), 400

    order = Order.query.get_or_404(order_id)
    order.order_status = new_status
    db.session.commit()
    return jsonify({'message': 'Status updated', 'order': order.to_dict()})


@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    from sqlalchemy import func
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
    pending_orders = Order.query.filter_by(order_status='pending').count()
    active_items = MenuItem.query.filter_by(is_available=True).count()
    return jsonify({
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'pending_orders': pending_orders,
        'active_menu_items': active_items
    })


# ─── Admin User Setup ────────────────────────────────────────────────────────

@admin_bp.route('/setup', methods=['POST'])
def setup_admin():
    """One-time setup to create the first admin user"""
    if AdminUser.query.count() > 0:
        return jsonify({'error': 'Admin already exists'}), 409
    data = request.get_json()
    admin = AdminUser(
        username=data['username'],
        role='superadmin'
    )
    admin.set_password(data['password'])
    db.session.add(admin)
    db.session.commit()
    return jsonify({'message': 'Admin created', 'admin': admin.to_dict()}), 201
