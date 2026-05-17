import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from bson.objectid import ObjectId

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    cards = db["cards"]
    card_id = ObjectId("6a09464842c5f2096ab6cc51")   # ← ObjectId
    now = datetime.utcnow()
    result = await cards.update_one(
        {"_id": card_id},
        {"$set": {"state": "review", "last_review": now, "due_date": now},
         "$inc": {"reps": 1}}
    )
    if result.modified_count:
        print(f"✅ Card reviewed. State: review, next review: {now}")
        updated = await cards.find_one({"_id": card_id})
        print("Updated card:", updated)
    else:
        print("❌ Card not found")

asyncio.run(main())