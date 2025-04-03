from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..db.session import Base
import enum

class RoleEnum(enum.Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    EDITOR = 'editor'
    VIEWER = 'viewer'

class WorldUser(Base):
    __tablename__ = "world_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False, index=True)
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.VIEWER)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships will be added later
    # user = relationship("User", back_populates="world_associations")
    # world = relationship("World", back_populates="user_associations") 