from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from auth.password_hasher import hash_password, verify_password
from auth.jwt_handler import create_access_token
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class SignupSchema(BaseModel):
    username: str
    password: str
    userType: Optional[int] = 3 

class LoginSchema(BaseModel):
    username: str
    password: str

class UserResponseSchema(BaseModel):
    id: str
    username: str
    userType: int
    created_at: Optional[str]

    class Config:
        orm_mode = True


@router.post("/signup")
def signup(payload: SignupSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter_by(username=payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = hash_password(payload.password)
    new_user = User(
        username=payload.username,
        password=hashed_pw,
        userType=payload.userType
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"user_id": new_user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "userType": new_user.userType,
        "userId": new_user.id 
    }


@router.post("/login")
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=payload.username).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "userType": user.userType,
        "userId": user.id 
    }

# View all users (excluding password)
@router.get("/view-all", response_model=List[UserResponseSchema])
def view_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
