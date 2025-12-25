# backend/create_tables.py
from .models import *          # imports model classes
from .database import Base, engine

if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")

class FileMeta(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer)
    content_type = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
