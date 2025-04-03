from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    world = relationship("World", back_populates="locations")
    parent_location = relationship("Location", remote_side=[id], back_populates="child_locations")
    child_locations = relationship("Location", back_populates="parent_location", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="location") # Items can exist without location?
    tags = relationship("LocationTag", back_populates="location", cascade="all, delete-orphan")

    # Relationships will be added later
    # world = relationship("World", back_populates="locations")
    # parent_location = relationship("Location", remote_side=[id], back_populates="child_locations")
    # child_locations = relationship("Location", back_populates="parent_location")
    # items = relationship("Item", back_populates="location")
    # tags = relationship("LocationTag", back_populates="location") 