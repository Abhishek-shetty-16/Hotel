-- Run this in psql as superuser
-- psql -U postgres -f setup_db.sql

CREATE DATABASE prakruthi_db;
CREATE USER prakruthi_user WITH ENCRYPTED PASSWORD 'prakruthi123';
GRANT ALL PRIVILEGES ON DATABASE prakruthi_db TO prakruthi_user;
ALTER DATABASE prakruthi_db OWNER TO prakruthi_user;

-- Connect to the database
\c prakruthi_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO prakruthi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO prakruthi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO prakruthi_user;

-- Drop and recreate schema for clean start (WARNING: deletes all data)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Re-grant privileges (if needed)
GRANT ALL ON SCHEMA public TO prakruthi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO prakruthi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO prakruthi_user;

-- Create tables matching models.py exactly

-- admin_users
CREATE TABLE admin_users (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT NOW()
);

-- customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- menu_items (FIX: includes id PK)
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_menu_items_category ON menu_items(category_id);
CREATE INDEX idx_menu_items_available ON menu_items(is_available);

-- carts
CREATE TABLE carts (
    cart_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_carts_customer ON carts(customer_id);

-- cart_items
CREATE TABLE cart_items (
    cart_item_id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(cart_id),
    item_id INTEGER NOT NULL REFERENCES menu_items(id),
    quantity INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_item ON cart_items(item_id);

-- orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    total_amount DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(20) DEFAULT 'pending',
    payment_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- order_items
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    item_id INTEGER NOT NULL REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_item ON order_items(item_id);

-- payments
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL REFERENCES orders(order_id),
    payment_method VARCHAR(50) DEFAULT 'razorpay',
    payment_status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    paid_at TIMESTAMP
);
CREATE INDEX idx_payments_order ON payments(order_id);

-- Seed categories
INSERT INTO categories (category_name, description) VALUES 
('Juices', 'Fresh fruit juices'),
('Snacks', 'Quick bites'),
('Meals', 'Full meals'),
('Beverages', 'Drinks'),
('Desserts', 'Sweet treats');
