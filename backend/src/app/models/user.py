from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from ..db.session import Base

class User(Base):
    __tablename__ = "users"  # Toto definuje název tabulky

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    characters = relationship("Character", back_populates="user")
    world_associations = relationship("WorldUser", back_populates="user")
    campaign_associations = relationship("UserCampaign", back_populates="user")
    availabilities = relationship("Availability", back_populates="user")
    images = relationship("Image", back_populates="user")

