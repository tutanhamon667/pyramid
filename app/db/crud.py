from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db.models import User, Wallet, Referral, Transaction
from app.db.schemas import UserCreate, WalletCreate

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        telegram_id=user.telegram_id,
        username=user.username,
        full_name=user.full_name,
        registration_date=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_wallet(db: Session, user_id: int) -> Optional[Wallet]:
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()

def create_wallet(db: Session, wallet: WalletCreate) -> Wallet:
    db_wallet = Wallet(
        user_id=wallet.user_id,
        btc_address=wallet.btc_address,
        usdt_address=wallet.usdt_address,
        lyc_address=wallet.lyc_address
    )
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def get_user_referrals(db: Session, user_id: int) -> List[Referral]:
    return db.query(Referral).filter(Referral.referrer_id == user_id).all()

def create_referral(db: Session, referrer_id: int, referred_id: int) -> Referral:
    db_referral = Referral(
        referrer_id=referrer_id,
        referred_id=referred_id,
        created_at=datetime.utcnow()
    )
    db.add(db_referral)
    db.commit()
    db.refresh(db_referral)
    return db_referral

def get_user_transactions(db: Session, user_id: int) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def create_transaction(
    db: Session, user_id: int, amount: float, currency: str, status: str = "pending"
) -> Transaction:
    db_transaction = Transaction(
        user_id=user_id,
        amount=amount,
        currency=currency,
        status=status
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
