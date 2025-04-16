from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    world = relationship("World", back_populates="campaigns")
    owner = relationship("User")
    user_associations = relationship("UserCampaign", back_populates="campaign", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="campaign", cascade="all, delete-orphan")
    campaign_invites = relationship("CampaignInvite", back_populates="campaign", cascade="all, delete-orphan")

    # Relationships will be added later
    # world = relationship("World", back_populates="campaigns")
    # user_associations = relationship("UserCampaign", back_populates="campaign")
    # sessions = relationship("Session", back_populates="campaign")
    # campaign_invites = relationship("CampaignInvite", back_populates="campaign") 