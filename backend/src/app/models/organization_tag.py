from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..db.session import Base

class OrganizationTag(Base):
    __tablename__ = "organization_tags"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    organization_tag_type_id = Column(Integer, ForeignKey("organization_tag_types.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships will be added later
    # organization = relationship("Organization", back_populates="tags")
    # tag_type = relationship("OrganizationTagType", back_populates="tags") 