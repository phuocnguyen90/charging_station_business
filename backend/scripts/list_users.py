import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db.session import SessionLocal
from models.user import User

def list_users():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Found {len(users)} users:")
    for u in users:
        print(f"- ID: {u.id}, Email: {u.email}, Role: {u.role}")
    db.close()

if __name__ == "__main__":
    list_users()
