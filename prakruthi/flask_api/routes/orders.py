from flask import Blueprint, request, jsonify
from models.models import Order, OrderItem, Cart, CartItem, MenuItem
from extensions import db

orders_bp = Blueprint('orders', __name__)

ORDER_STATUSES = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']


@orders_bp.route('/place', methods=['POST'])
def place_order():
    data = request.get_json()
    customer_id = data.get('customer_id')

    if not customer_id:
        return jsonify({'error': 'customer_id required'}), 400

    cart = Cart.query.filter_by(customer_id=customer_id).first()
    if not cart or not cart.items:
        return jsonify({'error': 'Cart is empty'}), 400

    total = sum(
        float(item.menu_item.price) * item.quantity
        for item in cart.items if item.menu_item
    )

    order = Order(
        customer_id=customer_id,
        total_amount=total,
        order_status='pending',
        payment_status='pending'
    )
    db.session.add(order)
    db.session.flush()

    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.order_id,
            item_id=cart_item.item_id,
            quantity=cart_item.quantity,
            price=cart_item.menu_item.price
        )
        db.session.add(order_item)

    CartItem.query.filter_by(cart_id=cart.cart_id).delete()
    db.session.commit()

    return jsonify({'message': 'Order placed', 'order': order.to_dict()}), 201


@orders_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())


@orders_bp.route('/all', methods=['GET'])
def get_all_orders():
    """Admin: get all orders"""
    status = request.args.get('status')
    if status:
        orders = Order.query.filter_by(order_status=status).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Admin: update order status"""
    data = request.get_json()
    new_status = data.get('order_status')

    if new_status not in ORDER_STATUSES:
        return jsonify({'error': f'Invalid status. Must be one of {ORDER_STATUSES}'}), 400

    order = Order.query.get_or_404(order_id)
    order.order_status = new_status
    db.session.commit()
    return jsonify({'message': 'Status updated', 'order': order.to_dict()})
