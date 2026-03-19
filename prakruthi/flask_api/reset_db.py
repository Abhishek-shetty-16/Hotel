"""
Run this ONCE to drop and recreate all Prakruthi tables.
    cd flask_api
    venv\Scripts\activate.bat
    python reset_db.py
"""
from app import create_app
from extensions import db
from models.models import (
    AdminUser, Customer, Category, MenuItem,
    Cart, CartItem, Order, OrderItem, Payment
)

app = create_app()

with app.app_context():
    print("Dropping Prakruthi tables with CASCADE...")

    tables = [
        'payments', 'order_items', 'orders',
        'cart_items', 'cart', 'menu_items',
        'categories', 'customers', 'admin_users'
    ]
    for t in tables:
        db.session.execute(db.text(f'DROP TABLE IF EXISTS "{t}" CASCADE;'))
    db.session.commit()
    print("All Prakruthi tables dropped.")

    print("Creating tables with correct schema...")
    db.create_all()
    print("Tables created!")

    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)

    # Verify menu_items has correct column names
    cols = [c['name'] for c in inspector.get_columns('menu_items')]
    print(f"\nmenu_items columns: {cols}")

    if 'item_id' in cols:
        print("SUCCESS - item_id column exists correctly!")
    else:
        print("ERROR - item_id not found, something is wrong.")

    print("\nDone! Now run: python app.py")
