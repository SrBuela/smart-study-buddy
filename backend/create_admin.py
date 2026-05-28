from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    YOUR_NAME = "Joseph Mercy Buela"
    YOUR_PASSWORD = "9840038816"
    YOUR_EMAIL = "srbuelajesu@gmail.com"
    
    # Delete if already exists
    User.query.filter_by(username=YOUR_NAME).delete()
    User.query.filter_by(email=YOUR_EMAIL).delete()
    
    # Create your admin account
    admin = User(
        username=YOUR_NAME,
        email=YOUR_EMAIL,
        password=generate_password_hash(YOUR_PASSWORD),
        total_points=0,
        total_studied=0,
        streak=0,
        unlocked_decks=999,
        stars=0
    )
    db.session.add(admin)
    db.session.commit()
    
    print("=" * 60)
    print("YOU ARE NOW AN ADMIN!")
    print("=" * 60)
    print(f"Username: {admin.username}")
    print(f"Password: {YOUR_PASSWORD}")
    print(f"Email: {admin.email}")
    print("=" * 60)
    print("\nLogin at: http://127.0.0.1:5000/login")
