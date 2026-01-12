import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from db.base import Base
from models.user import User
from core.security import get_password_hash

def seed_users():
    print("Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    users = [
        {"email": "admin@solar.com", "password": "admin123", "full_name": "Admin User", "role": "admin"},
        {"email": "installer@solar.com", "password": "installer123", "full_name": "Installer User", "role": "installer"},
        {"email": "client@solar.com", "password": "client123", "full_name": "Client User", "role": "client"},
    ]
    
    for u in users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                full_name=u["full_name"],
                role=u["role"]
            )
            db.add(user)
            print(f"Created {u['role']} user: {u['email']}")
        else:
            # Update password for existing user
            existing.hashed_password = get_password_hash(u["password"])
            print(f"Updated password for {u['role']} user: {u['email']}")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_users()
