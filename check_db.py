import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    names = await db.list_collection_names()
    print("Collections:", names)
    for col_name in names:
        col = db[col_name]
        doc = await col.find_one()
        if doc:
            print(f"Found doc in '{col_name}': _id={doc.get('_id')}, state={doc.get('state')}")
    # Specifically look for cards
    cards = db["cards"]
    doc = await cards.find_one()
    if doc:
        print(f"Card in 'cards': _id={doc['_id']}, state={doc.get('state')}")

asyncio.run(main())