from flask import Blueprint, request, jsonify, session
from models.models import Customer, AdminUser
from extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/customer/register', methods=['POST'])
def customer_register():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('phone'):
        return jsonify({'error': 'Name and phone are required'}), 400

    existing = Customer.query.filter_by(phone=data['phone']).first()
    if existing:
        return jsonify({'error': 'Phone number already registered'}), 409

    customer = Customer(
        name=data['name'],
        phone=data['phone'],
        email=data.get('email'),
        address=data.get('address')
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Registered successfully', 'customer': customer.to_dict()}), 201


@auth_bp.route('/customer/login', methods=['POST'])
def customer_login():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'Phone number is required'}), 400

    customer = Customer.query.filter_by(phone=phone).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    session['customer_id'] = customer.customer_id
    return jsonify({'message': 'Login successful', 'customer': customer.to_dict()})


@auth_bp.route('/customer/logout', methods=['POST'])
def customer_logout():
    session.pop('customer_id', None)
    return jsonify({'message': 'Logged out'})


@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin = AdminUser.query.filter_by(username=username).first()
    if not admin or not admin.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['admin_id'] = admin.admin_id
    session['admin_role'] = admin.role
    return jsonify({'message': 'Admin login successful', 'admin': admin.to_dict()})


@auth_bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_role', None)
    return jsonify({'message': 'Admin logged out'})


@auth_bp.route('/session', methods=['GET'])
def get_session():
    customer_id = session.get('customer_id')
    admin_id = session.get('admin_id')
    return jsonify({
        'customer_id': customer_id,
        'admin_id': admin_id,
        'is_admin': admin_id is not None
    })
