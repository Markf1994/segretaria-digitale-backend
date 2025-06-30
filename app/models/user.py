from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    todos = relationship("ToDo", back_populates="user")

