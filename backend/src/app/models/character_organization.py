from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..db.session import Base

class CharacterOrganization(Base):
    __tablename__ = "character_organizations"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships will be added later
    # character = relationship("Character", back_populates="organization_associations")
    # organization = relationship("Organization", back_populates="character_associations") 