from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.db import crud
from app.db.database import SessionLocal, engine
from app.db.models import Base
from app.db.schemas import User, UserCreate, Token, TokenData, Wallet, WalletCreate

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pyramid Marketing Bot",
    description="API for Telegram-based MLM platform with cryptocurrency payments",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, user.telegram_id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db, user)

@app.get("/api/v1/users/{telegram_id}", response_model=User)
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, telegram_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/api/v1/wallets/", response_model=Wallet)
def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db)):
    return crud.create_wallet(db, wallet)

@app.get("/api/v1/wallets/{user_id}", response_model=Wallet)
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    db_wallet = crud.get_user_wallet(db, user_id)
    if not db_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet

@app.get("/api/v1/referrals/{user_id}")
def get_referrals(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_referrals(db, user_id)
