import uuid
from sqlalchemy import Column, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

room_users = Table('room_users', Base.metadata,
    Column('room_id', String, ForeignKey('rooms.roomId')),
    Column('user_id', String, ForeignKey('users.userId'))
)

class Room(Base):
    __tablename__ = "rooms"

    roomId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    joinCode = Column(String, unique=True, index=True)
    isActive = Column(Boolean, default=True)
    
    users = relationship("User", secondary=room_users, backref="rooms")
    votes = relationship("Vote", back_populates="room")
    match_histories = relationship("MatchHistory", back_populates="room")
