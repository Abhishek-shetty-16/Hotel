from app import create_app
from extensions import db
from models.models import AdminUser

app = create_app()

with app.app_context():
    existing = AdminUser.query.filter_by(username='admin').first()
    if existing:
        AdminUser.query.delete()
        db.session.commit()
        print("Old admin deleted.")

    admin = AdminUser(username='admin', role='superadmin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()

    verify = AdminUser.query.filter_by(username='admin').first()
    print(f"Admin created: {verify.username}")
    print(f"Password works: {verify.check_password('admin123')}")