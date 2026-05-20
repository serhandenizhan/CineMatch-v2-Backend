from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import uuid
import string
import random
from app.core.database import get_db
from app.models.models import Room, User
from app.services.tmdb_fetcher import fetch_popular_movies

router = APIRouter()

def generate_join_code(length=6):
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

@router.post("/create")
def create_room(user_id: str, filter_type: str = "popular", db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.userId == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    join_code = generate_join_code()
    while db.query(Room).filter(Room.joinCode == join_code).first():
        join_code = generate_join_code()
        
    new_room = Room(joinCode=join_code, filterType=filter_type)
    new_room.users.append(db_user)
    
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    
    return {"room_id": new_room.roomId, "join_code": new_room.joinCode}

@router.post("/join")
def join_room(join_code: str, user_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.joinCode == join_code, Room.isActive == True).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found or inactive")
        
    db_user = db.query(User).filter(User.userId == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if db_user not in db_room.users:
        db_room.users.append(db_user)
        db.commit()
        
    return {"room_id": db_room.roomId, "message": "Joined successfully"}

room_movie_cache = {}

@router.get("/{room_id}/movies")
async def get_room_movies(room_id: str, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.roomId == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    if len(db_room.users) < 2:
        return {"status": "waiting", "movies": []}
        
    if room_id in room_movie_cache:
        return {"status": "success", "movies": room_movie_cache[room_id]}
        
    movies = await fetch_popular_movies(db_room.filterType)
    if not movies:
        return {"status": "waiting", "movies": []}
        
    room_movie_cache[room_id] = movies
    return {"status": "success", "movies": movies}
