from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfileUpdate(BaseModel):
    favorite_genres: List[str]
    favorite_directors: List[str]
    watch_history: List[str]

class VoteSubmit(BaseModel):
    user_id: str
    movie_id: str
    vote_status: str # 'yes' or 'no'

class MatchLogResponse(BaseModel):
    match_id: str
    room_id: str
    movie_id: str
    matched_at: datetime
