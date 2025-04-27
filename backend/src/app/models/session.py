from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    summary = Column(Text)
    date_time = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="sessions")
    character_associations = relationship("SessionCharacter", back_populates="session", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="session") # ondelete="SET NULL" handled in JournalEntry 
    
    # New relationship for availability slots
    availability_slots = relationship(
        "SessionSlot",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin"
    ) 