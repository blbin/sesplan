from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class World(Base):
    __tablename__ = "worlds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    is_private = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    characters = relationship("Character", back_populates="world")
    user_associations = relationship("WorldUser", back_populates="world")
    images = relationship("Image", back_populates="world")
    campaigns = relationship("Campaign", back_populates="world")
    events = relationship("Event", back_populates="world")
    locations = relationship("Location", back_populates="world")
    organizations = relationship("Organization", back_populates="world")
    character_tag_types = relationship("CharacterTagType", back_populates="world")
    item_tag_types = relationship("ItemTagType", back_populates="world")
    location_tag_types = relationship("LocationTagType", back_populates="world")
    organization_tag_types = relationship("OrganizationTagType", back_populates="world")
    world_invites = relationship("WorldInvite", back_populates="world")

    # Relationships will be added later
    # characters = relationship("Character", back_populates="world")
    # user_associations = relationship("WorldUser", back_populates="world")
    # images = relationship("Image", back_populates="world")
    # campaigns = relationship("Campaign", back_populates="world")
    # events = relationship("Event", back_populates="world")
    # locations = relationship("Location", back_populates="world")
    # organizations = relationship("Organization", back_populates="world")
    # character_tag_types = relationship("CharacterTagType", back_populates="world")
    # item_tag_types = relationship("ItemTagType", back_populates="world")
    # location_tag_types = relationship("LocationTagType", back_populates="world")
    # organization_tag_types = relationship("OrganizationTagType", back_populates="world")
    # world_invites = relationship("WorldInvite", back_populates="world") 