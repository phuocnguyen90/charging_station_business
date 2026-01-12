from sqlalchemy import Boolean, Column, Integer, String, Enum
from db.base import Base
import enum

class UserRole(str, enum.Enum):
    CLIENT = "client"
    INSTALLER = "installer"
    ADMIN = "admin"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    role = Column(String, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
