from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import VoteSubmit, MatchLogResponse
from app.models.models import Vote, MatchHistory, Room, Movie
from typing import List

router = APIRouter()

@router.post("/{room_id}/vote")
def submit_vote(room_id: str, vote: VoteSubmit, db: Session = Depends(get_db)):
    # Check if room exists
    db_room = db.query(Room).filter(Room.roomId == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    # Record the vote
    new_vote = Vote(
        userId=vote.user_id,
        roomId=room_id,
        movieId=vote.movie_id,
        status=vote.vote_status
    )
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    
    # Evaluate Consensus Logic from the Process View
    if vote.vote_status == 'yes':
        yes_votes = db.query(Vote).filter(
            Vote.roomId == room_id,
            Vote.movieId == vote.movie_id,
            Vote.status == 'yes'
        ).all()
        
        # Determine unique users who voted yes
        yes_user_ids = set([v.userId for v in yes_votes])
        
        # In a real app we might check if they are the exact users in the room
        # But per the logic: if len >= 2, we have a match
        if len(yes_user_ids) >= 2: # Consensus Met
            # Ensure we haven't already matched this
            existing_match = db.query(MatchHistory).filter(
                MatchHistory.roomId == room_id,
                MatchHistory.matchedMovieId == vote.movie_id
            ).first()
            
            if not existing_match:
                # Trigger Historic Match Logging Workflow
                new_match = MatchHistory(roomId=room_id, matchedMovieId=vote.movie_id)
                db.add(new_match)
                db.commit()
                db.refresh(new_match)
                
                match_record = {
                    "match_id": new_match.matchId,
                    "room_id": new_match.roomId,
                    "movie_id": new_match.matchedMovieId,
                    "matched_at": new_match.matchedAt
                }
                return {"is_matched": True, "match_details": match_record}
            else:
                return {"is_matched": True, "message": "Already matched previously"}
                
    return {"is_matched": False, "message": "Vote recorded."}

import httpx
import asyncio
from app.services.tmdb_fetcher import fetch_movie_details, TMDB_API_KEY, BASE_URL

@router.get("/users/{user_id}/matches")
async def get_user_match_history(user_id: str, db: Session = Depends(get_db)):
    rooms_for_user = db.query(Room).filter(Room.users.any(userId=user_id)).all()
    room_ids = [room.roomId for room in rooms_for_user]
    
    matches = db.query(MatchHistory).filter(MatchHistory.roomId.in_(room_ids)).all()
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_movie_details(client, match.matchedMovieId) for match in matches]
        details_results = await asyncio.gather(*tasks)
        
    result = []
    for match, details in zip(matches, details_results):
        movie_title = "Unknown"
        poster_url = "https://via.placeholder.com/500x750?text=No+Poster"
        if details:
            movie_title = details.get('title', 'Unknown')
            if details.get('poster_path'):
                poster_url = f"https://image.tmdb.org/t/p/w500{details.get('poster_path')}"
                
        result.append({
            "match_id": match.matchId,
            "room_id": match.roomId,
            "movie_id": match.matchedMovieId,
            "matched_at": match.matchedAt,
            "movie_title": movie_title,
            "poster_url": poster_url
        })
        
    return result

@router.get("/users/{user_id}/liked")
async def get_user_liked_movies(user_id: str, db: Session = Depends(get_db)):
    likes = db.query(Vote).filter(Vote.userId == user_id, Vote.status == 'yes').all()
    
    # Deduplicate movie IDs
    unique_movie_ids = list(set([vote.movieId for vote in likes]))
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_movie_details(client, movie_id) for movie_id in unique_movie_ids]
        details_results = await asyncio.gather(*tasks)
        
    result = []
    for movie_id, details in zip(unique_movie_ids, details_results):
        movie_title = "Unknown"
        poster_url = "https://via.placeholder.com/500x750?text=No+Poster"
        if details:
            movie_title = details.get('title', 'Unknown')
            if details.get('poster_path'):
                poster_url = f"https://image.tmdb.org/t/p/w500{details.get('poster_path')}"
                
        result.append({
            "movie_id": movie_id,
            "movie_title": movie_title,
            "poster_url": poster_url
        })
        
    return result
