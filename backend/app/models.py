from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from .database import Base

class FileMeta(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False, unique=True)  # local path or S3 key
    size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
