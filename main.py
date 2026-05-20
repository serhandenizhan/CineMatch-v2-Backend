from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, rooms, votes
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CineMatch-V2 API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth.router, prefix="/api/user", tags=["user"]) # to handle /api/user/profile mapped in auth router for now
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(votes.router, prefix="/api/votes", tags=["votes"])

@app.get("/")
def root():
    return {"message": "Welcome to CineMatch-V2 Backend"}
