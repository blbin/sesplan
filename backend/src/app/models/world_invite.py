from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class WorldInvite(Base):
    __tablename__ = "world_invites"

    id = Column(Integer, primary_key=True, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    uses = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships will be added later
    # world = relationship("World", back_populates="world_invites") 