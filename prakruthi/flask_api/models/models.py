from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    admin_id      = db.Column('admin_id', db.Integer, primary_key=True, autoincrement=True)
    username      = db.Column('username', db.String(100), unique=True, nullable=False)
    password_hash = db.Column('password_hash', db.Text, nullable=False)
    role          = db.Column('role', db.String(50), default='admin')
    created_at    = db.Column('created_at', db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'admin_id':   self.admin_id,
            'username':   self.username,
            'role':       self.role,
            'created_at': self.created_at.isoformat()
        }


class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column('customer_id', db.Integer, primary_key=True, autoincrement=True)
    name        = db.Column('name',  db.String(100), nullable=False)
    phone       = db.Column('phone', db.String(15),  unique=True, nullable=False)
    email       = db.Column('email', db.String(150), unique=True)
    address     = db.Column('address', db.Text)
    created_at  = db.Column('created_at', db.DateTime, default=datetime.utcnow)

    carts  = db.relationship('Cart',  backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name':        self.name,
            'phone':       self.phone,
            'email':       self.email,
            'address':     self.address,
            'created_at':  self.created_at.isoformat()
        }


class Category(db.Model):
    __tablename__ = 'categories'

    category_id   = db.Column('category_id',   db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column('category_name', db.String(100), nullable=False)

    items = db.relationship('MenuItem', backref='category', lazy=True)

    def to_dict(self):
        return {
            'category_id':   self.category_id,
            'category_name': self.category_name
        }


class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    item_id      = db.Column('item_id',      db.Integer, primary_key=True, autoincrement=True)
    name         = db.Column('name',         db.String(150), nullable=False)
    description  = db.Column('description',  db.Text)
    price        = db.Column('price',        db.Numeric(10, 2), nullable=False)
    category_id  = db.Column('category_id',  db.Integer, db.ForeignKey('categories.category_id'))
    image_url    = db.Column('image_url',    db.Text)
    is_available = db.Column('is_available', db.Boolean, default=True)
    created_at   = db.Column('created_at',   db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'item_id':       self.item_id,
            'name':          self.name,
            'description':   self.description,
            'price':         float(self.price),
            'category_id':   self.category_id,
            'category_name': self.category.category_name if self.category else None,
            'image_url':     self.image_url,
            'is_available':  self.is_available,
            'created_at':    self.created_at.isoformat()
        }


class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id     = db.Column('cart_id',     db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column('customer_id', db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    created_at  = db.Column('created_at',  db.DateTime, default=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'cart_id':     self.cart_id,
            'customer_id': self.customer_id,
            'created_at':  self.created_at.isoformat(),
            'items':       [item.to_dict() for item in self.items]
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    cart_item_id = db.Column('cart_item_id', db.Integer, primary_key=True, autoincrement=True)
    cart_id      = db.Column('cart_id',      db.Integer, db.ForeignKey('cart.cart_id'), nullable=False)
    item_id      = db.Column('item_id',      db.Integer, db.ForeignKey('menu_items.item_id'), nullable=False)
    quantity     = db.Column('quantity',     db.Integer, nullable=False, default=1)

    menu_item = db.relationship('MenuItem', lazy=True)

    def to_dict(self):
        return {
            'cart_item_id': self.cart_item_id,
            'cart_id':      self.cart_id,
            'item_id':      self.item_id,
            'quantity':     self.quantity,
            'menu_item':    self.menu_item.to_dict() if self.menu_item else None
        }


class Order(db.Model):
    __tablename__ = 'orders'

    order_id       = db.Column('order_id',       db.Integer, primary_key=True, autoincrement=True)
    customer_id    = db.Column('customer_id',    db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    total_amount   = db.Column('total_amount',   db.Numeric(10, 2), nullable=False)
    order_status   = db.Column('order_status',   db.String(50), default='pending')
    payment_status = db.Column('payment_status', db.String(50), default='pending')
    created_at     = db.Column('created_at',     db.DateTime, default=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    payment     = db.relationship('Payment',   backref='order', lazy=True, uselist=False)

    def to_dict(self):
        return {
            'order_id':       self.order_id,
            'customer_id':    self.customer_id,
            'customer_name':  self.customer.name if self.customer else None,
            'total_amount':   float(self.total_amount),
            'order_status':   self.order_status,
            'payment_status': self.payment_status,
            'created_at':     self.created_at.isoformat(),
            'order_items':    [item.to_dict() for item in self.order_items],
            'payment':        self.payment.to_dict() if self.payment else None
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    order_item_id = db.Column('order_item_id', db.Integer, primary_key=True, autoincrement=True)
    order_id      = db.Column('order_id',      db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    item_id       = db.Column('item_id',       db.Integer, db.ForeignKey('menu_items.item_id'), nullable=False)
    quantity      = db.Column('quantity',      db.Integer, nullable=False)
    price         = db.Column('price',         db.Numeric(10, 2), nullable=False)

    menu_item = db.relationship('MenuItem', lazy=True)

    def to_dict(self):
        return {
            'order_item_id': self.order_item_id,
            'order_id':      self.order_id,
            'item_id':       self.item_id,
            'quantity':      self.quantity,
            'price':         float(self.price),
            'item_name':     self.menu_item.name if self.menu_item else None
        }


class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id     = db.Column('payment_id',     db.Integer, primary_key=True, autoincrement=True)
    order_id       = db.Column('order_id',       db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    payment_method = db.Column('payment_method', db.String(50), default='razorpay')
    payment_status = db.Column('payment_status', db.String(50), default='pending')
    transaction_id = db.Column('transaction_id', db.String(255))
    paid_at        = db.Column('paid_at',        db.DateTime)

    def to_dict(self):
        return {
            'payment_id':     self.payment_id,
            'order_id':       self.order_id,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'paid_at':        self.paid_at.isoformat() if self.paid_at else None
        }
