import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sql_app.db')}"
# POSTGRES_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLITE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
