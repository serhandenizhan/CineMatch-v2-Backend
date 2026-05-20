from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UserRegister, UserLogin, UserProfileUpdate
from app.models.models import User, UserProfile
from app.core.jwt_handler import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    if len(user.password) > 70:
        raise HTTPException(status_code=400, detail="Password must be less than 72 characters.")
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, passwordHash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize empty profile
    new_profile = UserProfile(userId=new_user.userId)
    db.add(new_profile)
    db.commit()

    return {"user_id": new_user.userId, "message": "User registered successfully"}

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.passwordHash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": db_user.userId})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.userId}

@router.post("/profile")
def update_profile(user_id: str, profile: UserProfileUpdate, db: Session = Depends(get_db)):
    db_profile = db.query(UserProfile).filter(UserProfile.userId == user_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    db_profile.favoriteGenres = ",".join(profile.favorite_genres)
    db_profile.favoriteDirectors = ",".join(profile.favorite_directors)
    db_profile.watchHistory = ",".join(profile.watch_history)
    db.commit()
    
    return {"status": "Profile updated successfully"}
