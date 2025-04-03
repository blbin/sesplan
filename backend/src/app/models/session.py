from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    summary = Column(Text)
    date_time = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships will be added later
    # campaign = relationship("Campaign", back_populates="sessions")
    # character_associations = relationship("SessionCharacter", back_populates="session")
    # availabilities = relationship("Availability", back_populates="session")
    # journal_entries = relationship("JournalEntry", back_populates="session") 