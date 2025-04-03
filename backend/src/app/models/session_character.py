from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..db.session import Base

class SessionCharacter(Base):
    __tablename__ = "session_characters"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships will be added later
    # session = relationship("Session", back_populates="character_associations")
    # character = relationship("Character", back_populates="session_associations") 