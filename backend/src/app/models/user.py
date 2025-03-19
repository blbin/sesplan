from sqlalchemy import Column, Integer, String
from app.db.session import Base

class User(Base):
    __tablename__ = "users"  # Toto definuje název tabulky

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

