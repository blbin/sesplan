from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="SET NULL"), index=True, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), index=True, nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    world = relationship("World", back_populates="items")
    character = relationship("Character", back_populates="items")
    location = relationship("Location", back_populates="items")
    tags = relationship("ItemTag", back_populates="item", cascade="all, delete-orphan")

    # Relationships will be added later
    # character = relationship("Character", back_populates="items")
    # location = relationship("Location", back_populates="items")
    # tags = relationship("ItemTag", back_populates="item") 