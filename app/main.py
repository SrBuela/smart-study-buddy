from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database import init_db
from app.routes import auth, cards, decks, ai, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Smart Study Buddy API...")
    await init_db()
    print("Database initialized successfully")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Smart Study Buddy API",
    description="AI-powered spaced repetition system using FSRS algorithm",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(decks.router)
app.include_router(cards.router)
app.include_router(ai.router)
app.include_router(analytics.router)

@app.get("/")
async def root():
    return {
        "message": "Smart Study Buddy API",
        "algorithm": "FSRS (Free Spaced Repetition Scheduler)",
        "features": [
            "Personalized spaced repetition",
            "AI flashcard generation",
            "Weak topic detection",
            "Memory prediction",
            "Study analytics"
        ],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}