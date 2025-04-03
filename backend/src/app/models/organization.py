from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    world = relationship("World", back_populates="organizations")
    parent_organization = relationship("Organization", remote_side=[id], back_populates="child_organizations")
    child_organizations = relationship("Organization", back_populates="parent_organization", cascade="all, delete-orphan")
    character_associations = relationship("CharacterOrganization", back_populates="organization", cascade="all, delete-orphan")
    tags = relationship("OrganizationTag", back_populates="organization", cascade="all, delete-orphan")

    # Relationships will be added later
    # world = relationship("World", back_populates="organizations")
    # parent_organization = relationship("Organization", remote_side=[id], back_populates="child_organizations")
    # child_organizations = relationship("Organization", back_populates="parent_organization")
    # character_associations = relationship("CharacterOrganization", back_populates="organization")
    # tags = relationship("OrganizationTag", back_populates="organization") 