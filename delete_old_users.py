import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    result = await db.users.delete_many({})
    print(f"Deleted {result.deleted_count} users.")
    client.close()

asyncio.run(main())