import sys
sys.path.insert(0, r'C:\Users\joseph\smart_study_buddy\backend')

from app import app
from models import User, Deck, Card

print("=" * 60)
print("CHECKING USERS AND DECKS")
print("=" * 60)

with app.app_context():
    users = User.query.filter(User.username != 'Joseph Mercy Buela', User.username != 'admin').all()
    
    for user in users:
        deck_count = Deck.query.filter_by(user_id=user.id).count()
        print(f"{user.username}: {deck_count} decks")
    
    print("\n" + "=" * 60)
    print("To add decks for a specific user, run: python add_decks_for_user.py USERNAME")
    print("=" * 60)
