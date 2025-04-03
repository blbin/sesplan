from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..db.session import Base

class LocationTag(Base):
    __tablename__ = "location_tags"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    location_tag_type_id = Column(Integer, ForeignKey("location_tag_types.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    location = relationship("Location", back_populates="tags")
    tag_type = relationship("LocationTagType", back_populates="tags") 