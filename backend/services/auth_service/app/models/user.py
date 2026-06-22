from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "gen_auth"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="Scientist", nullable=False)  # Scientist, Project Lead, Administrator, External Collaborator
    is_active = Column(Boolean, default=True, nullable=False)

    roles = relationship("Role", secondary="gen_auth.user_roles", back_populates="users")
