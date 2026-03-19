from flask import Blueprint, request, jsonify
from extensions import db
from models.models import Payment, Order
from datetime import datetime
import uuid

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/create-order', methods=['POST'])
def create_payment_order():
    data = request.get_json()
    order_id = data.get('order_id')

    order = Order.query.get_or_404(order_id)

    if order.payment_status == 'paid':
        return jsonify({'error': 'Order already paid'}), 400

    # Generate a transaction reference
    txn_ref = f"TXN-{order_id}-{uuid.uuid4().hex[:8].upper()}"

    payment = Payment.query.filter_by(order_id=order_id).first()
    if not payment:
        payment = Payment(
            order_id=order_id,
            payment_method='pending',
            payment_status='pending',
            transaction_id=txn_ref
        )
        db.session.add(payment)
    else:
        payment.transaction_id = txn_ref
        payment.payment_status = 'pending'

    db.session.commit()

    return jsonify({
        'order_id':    order_id,
        'amount':      float(order.total_amount),
        'txn_ref':     txn_ref,
        'customer_id': order.customer_id
    })


@payments_bp.route('/confirm', methods=['POST'])
def confirm_payment():
    """Called after user selects payment method and confirms"""
    data = request.get_json()
    order_id       = data.get('order_id')
    payment_method = data.get('payment_method')  # upi / card / cod
    txn_ref        = data.get('txn_ref')

    payment = Payment.query.filter_by(order_id=order_id).first()
    if payment:
        payment.payment_method = payment_method
        payment.payment_status = 'paid'
        payment.transaction_id = txn_ref
        payment.paid_at        = datetime.utcnow()

    order = Order.query.get(order_id)
    if order:
        order.payment_status = 'paid'
        order.order_status   = 'confirmed'

    db.session.commit()
    return jsonify({'message': 'Payment confirmed', 'order_id': order_id})


@payments_bp.route('/failure', methods=['POST'])
def payment_failure():
    data     = request.get_json()
    order_id = data.get('order_id')

    payment = Payment.query.filter_by(order_id=order_id).first()
    if payment:
        payment.payment_status = 'failed'

    order = Order.query.get(order_id)
    if order:
        order.payment_status = 'failed'

    db.session.commit()
    return jsonify({'message': 'Payment failure recorded'})


@payments_bp.route('/<int:order_id>', methods=['GET'])
def get_payment(order_id):
    payment = Payment.query.filter_by(order_id=order_id).first_or_404()
    return jsonify(payment.to_dict())
