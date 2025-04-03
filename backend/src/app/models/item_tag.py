from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..db.session import Base

class ItemTag(Base):
    __tablename__ = "item_tags"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True)
    item_tag_type_id = Column(Integer, ForeignKey("item_tag_types.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    item = relationship("Item", back_populates="tags")
    tag_type = relationship("ItemTagType", back_populates="tags") 