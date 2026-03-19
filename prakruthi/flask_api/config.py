import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prakruthi-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:1234@localhost:5432/hotel'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_YOUR_KEY_ID')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'YOUR_KEY_SECRET')
