from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships will be added later
    # user = relationship("User", back_populates="characters")
    # world = relationship("World", back_populates="characters")
    # journal = relationship("Journal", back_populates="character", uselist=False)
    # organization_associations = relationship("CharacterOrganization", back_populates="character")
    # tags = relationship("CharacterTag", back_populates="character")
    # items = relationship("Item", back_populates="character")
    # session_associations = relationship("SessionCharacter", back_populates="character") 