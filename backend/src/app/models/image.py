from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..db.session import Base
import enum

class TargetTypeEnum(enum.Enum):
    WORLD = 'world'
    CHARACTER = 'character'
    ITEM = 'item'
    LOCATION = 'location'
    ORGANIZATION = 'organization'
    EVENT = 'event'
    CAMPAIGN = 'campaign'
    SESSION = 'session'
    # Add other target types as needed

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), index=True)
    target_id = Column(Integer, nullable=False, index=True)
    target_type = Column(SQLEnum(TargetTypeEnum), nullable=False, index=True)
    url = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships will be added later
    # user = relationship("User", back_populates="images")
    # world = relationship("World", back_populates="images")
    # Generic relationship needs to be handled in the application logic 