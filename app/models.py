from sqlalchemy import Column, BLOB, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from passlib.hash import bcrypt
from datetime import datetime
from .database import Base

class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(150), unique=True, nullable=False)
    realname = Column(String(150), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_name = Column(String(255), unique=True, nullable=False)
    rec_size = Column(String(255), nullable=True, default="5 gallons")
    ingredients = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)

    batches = relationship("Batch", back_populates="recipe")

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    primary_fermentation = Column(Date, nullable=True)
    secondary_fermentation = Column(Date, nullable=True)
    bottled = Column(Date, nullable=True)
    batch_size = Column(String(255), nullable=True, default="5 gallons")
    notes = Column(Text, nullable=True)
    osg = Column(String(24), nullable=True)
    fsg = Column(String(24), nullable=True)
    abv = Column(String(24), nullable=True)
    image = Column(BLOB, nullable=True)

    recipe = relationship("Recipe", back_populates="batches")
