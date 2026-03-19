from flask import Blueprint, request, jsonify
from models.models import Cart, CartItem, MenuItem
from extensions import db

cart_bp = Blueprint('cart', __name__)


def get_or_create_cart(customer_id):
    cart = Cart.query.filter_by(customer_id=customer_id).first()
    if not cart:
        cart = Cart(customer_id=customer_id)
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.route('/<int:customer_id>', methods=['GET'])
def get_cart(customer_id):
    cart = get_or_create_cart(customer_id)
    return jsonify(cart.to_dict())


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    customer_id = data.get('customer_id')
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)

    if not customer_id or not item_id:
        return jsonify({'error': 'customer_id and item_id required'}), 400

    menu_item = MenuItem.query.get(item_id)
    if not menu_item or not menu_item.is_available:
        return jsonify({'error': 'Item not available'}), 404

    cart = get_or_create_cart(customer_id)

    existing = CartItem.query.filter_by(cart_id=cart.cart_id, item_id=item_id).first()
    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.cart_id, item_id=item_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': 'Added to cart', 'cart': cart.to_dict()})


@cart_bp.route('/update', methods=['PUT'])
def update_cart_item():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    quantity = data.get('quantity')

    cart_item = CartItem.query.get_or_404(cart_item_id)
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    db.session.commit()
    return jsonify({'message': 'Cart updated'})


@cart_bp.route('/remove/<int:cart_item_id>', methods=['DELETE'])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed'})


@cart_bp.route('/clear/<int:customer_id>', methods=['DELETE'])
def clear_cart(customer_id):
    cart = Cart.query.filter_by(customer_id=customer_id).first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.cart_id).delete()
        db.session.commit()
    return jsonify({'message': 'Cart cleared'})
