from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Delete existing user if exists
    User.query.filter_by(username='Joseph Mercy Buela').delete()
    
    # Create new admin user
    admin = User(
        username='Joseph Mercy Buela',
        email='admin@college.edu',
        password=generate_password_hash('9840038816'),
        total_points=0,
        total_studied=0,
        streak=0,
        unlocked_decks=999,
        stars=0
    )
    db.session.add(admin)
    db.session.commit()
    print("=" * 50)
    print("Admin user created successfully!")
    print("=" * 50)
    print("Username: Joseph Mercy Buela")
    print("Password: 9840038816")
    print("=" * 50)
