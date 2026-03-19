from flask import Blueprint, request, jsonify
from models.models import MenuItem, Category

menu_bp = Blueprint('menu', __name__)


@menu_bp.route('/', methods=['GET'])
def get_menu():
    category_id = request.args.get('category_id')
    if category_id:
        items = MenuItem.query.filter_by(category_id=category_id, is_available=True).all()
    else:
        items = MenuItem.query.filter_by(is_available=True).all()
    return jsonify([item.to_dict() for item in items])


@menu_bp.route('/all', methods=['GET'])
def get_all_items():
    """Admin: get all items including unavailable"""
    items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in items])


@menu_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@menu_bp.route('/categories', methods=['GET'])
def get_categories():
    cats = Category.query.all()
    return jsonify([c.to_dict() for c in cats])
