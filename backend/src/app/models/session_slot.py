from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .session import Session  # noqa: F401
    from .user_availability import UserAvailability # noqa: F401

class SessionSlot(Base):
    __tablename__ = "session_slots"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_from = Column(DateTime(timezone=True), nullable=False)
    slot_to = Column(DateTime(timezone=True), nullable=False)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    session = relationship("Session", back_populates="availability_slots")
    user_availabilities = relationship(
        "UserAvailability", 
        back_populates="slot", 
        cascade="all, delete-orphan",
        lazy="selectin" # Efficient loading of related availabilities
    ) 