from typing import Optional
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings


class AuthService:
    @staticmethod
    async def create_user(email: str, username: str, password: str, full_name: Optional[str] = None) -> User:
        # Check if user exists
        existing_user = await User.find_one({"email": email})
        if existing_user:
            raise ValueError("Email already registered")

        # Create user
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            full_name=full_name
        )
        await user.insert()
        return user

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        user = await User.find_one({"email": email})
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def login(email: str, password: str) -> dict:
        user = await AuthService.authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid email or password")

        # Update streak
        await AuthService.update_streak(user)

        # Create token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    async def update_streak(user: User):
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        if user.last_study_date:
            last_date = user.last_study_date.date()
            today = now.date()

            if last_date == today - timedelta(days=1):
                user.streak += 1
            elif last_date != today:
                user.streak = 1

            user.longest_streak = max(user.longest_streak, user.streak)
        else:
            user.streak = 1

        user.last_study_date = now
        await user.save()