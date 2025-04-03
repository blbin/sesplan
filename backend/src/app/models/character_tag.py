from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..db.session import Base

class CharacterTag(Base):
    __tablename__ = "character_tags"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    character_tag_type_id = Column(Integer, ForeignKey("character_tag_types.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    character = relationship("Character", back_populates="tags")
    tag_type = relationship("CharacterTagType", back_populates="tags") 