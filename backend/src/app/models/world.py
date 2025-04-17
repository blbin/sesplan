from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class World(Base):
    __tablename__ = "worlds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user_associations = relationship("WorldUser", back_populates="world", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="world", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="world", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="world", cascade="all, delete-orphan")
    organizations = relationship("Organization", back_populates="world", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="world", cascade="all, delete-orphan")
    world_invites = relationship("WorldInvite", back_populates="world", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="world", cascade="all, delete-orphan")
    character_tag_types = relationship("CharacterTagType", back_populates="world")
    item_tag_types = relationship("ItemTagType", back_populates="world")
    location_tag_types = relationship("LocationTagType", back_populates="world")
    organization_tag_types = relationship("OrganizationTagType", back_populates="world")

    # Example of getting the owner through the association (if needed elsewhere)
    # @property
    # def owner(self):
    #     for assoc in self.user_associations:
    #         if assoc.role == RoleEnum.OWNER:
    #             return assoc.user
    #     return None

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