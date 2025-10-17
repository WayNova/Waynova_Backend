from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import UserRegister, UserLogin, Token
from .auth_utils import hash_password, verify_password, create_access_token
from .models import User
from db.database import get_db

router = APIRouter()

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        mobile=user.mobile,
        password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    return {"message": "User account created successfully"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
