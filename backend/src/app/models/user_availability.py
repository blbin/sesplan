from sqlalchemy import Column, Integer, Text, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .session_slot import SessionSlot # noqa: F401

class UserAvailability(Base):
    __tablename__ = "user_availabilities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("session_slots.id", ondelete="CASCADE"), nullable=False, index=True)
    available_from = Column(DateTime(timezone=True), nullable=False)
    available_to = Column(DateTime(timezone=True), nullable=False)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="user_availabilities")
    slot = relationship("SessionSlot", back_populates="user_availabilities")

    # Constraint: A user can only have one availability record per slot
    __table_args__ = (UniqueConstraint('user_id', 'slot_id', name='uq_user_slot_availability'),) 