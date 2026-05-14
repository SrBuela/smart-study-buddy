# Test if basic imports work
print("Testing Python setup...")

try:
    import fastapi
    print("✅ FastAPI installed - version:", fastapi.__version__)
except ImportError as e:
    print("❌ FastAPI not installed:", e)

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    print("✅ Motor (MongoDB) installed")
except ImportError as e:
    print("❌ Motor not installed:", e)

try:
    from beanie import Document, init_beanie
    print("✅ Beanie installed")
except ImportError as e:
    print("❌ Beanie not installed:", e)

try:
    from pydantic import BaseModel
    print("✅ Pydantic installed")
except ImportError as e:
    print("❌ Pydantic not installed:", e)

try:
    from fsrs import FSRS
    print("✅ FSRS installed")
except ImportError as e:
    print("❌ FSRS not installed:", e)

print("\nTest complete!")