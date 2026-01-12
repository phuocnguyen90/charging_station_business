import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.user import User
import argparse

def promote_to_admin(email: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"User with email {email} not found.")
        return
    
    user.role = "admin"
    db.commit()
    print(f"User {email} is now an ADMIN.")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 create_admin.py <email>")
        sys.exit(1)
        
    email = sys.argv[1]
    promote_to_admin(email)
