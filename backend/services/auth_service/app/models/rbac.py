from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "gen_auth"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    permissions = relationship("Permission", secondary="gen_auth.role_permissions", back_populates="roles")
    users = relationship("User", secondary="gen_auth.user_roles", back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "gen_auth"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    roles = relationship("Role", secondary="gen_auth.role_permissions", back_populates="permissions")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "gen_auth"}

    role_id = Column(Integer, ForeignKey("gen_auth.roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("gen_auth.permissions.id", ondelete="CASCADE"), primary_key=True)


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "gen_auth"}

    user_id = Column(Integer, ForeignKey("gen_auth.users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("gen_auth.roles.id", ondelete="CASCADE"), primary_key=True)
