import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
from passlib.context import CryptContext
from database.database import SessionLocal
from database.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

default_username = "admin@gmail.com"
default_password = "admin123"
default_user_type = 1

existing_user = db.query(User).filter_by(username=default_username).first()

if existing_user:
    print(f"User {default_username} already exists.")
else:
    admin_user = User(
        id=str(uuid.uuid4()),
        username=default_username,
        password=pwd_context.hash(default_password),
        userType=default_user_type
    )
    db.add(admin_user)
    db.commit()
    print(f"Default admin user {default_username} created successfully.")
