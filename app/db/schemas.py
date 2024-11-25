from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    registration_date: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

class WalletBase(BaseModel):
    user_id: int
    btc_address: Optional[str] = None
    usdt_address: Optional[str] = None
    lyc_address: Optional[str] = None

class WalletCreate(WalletBase):
    pass

class Wallet(WalletBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReferralBase(BaseModel):
    referrer_id: int
    referred_id: int

class ReferralCreate(ReferralBase):
    pass

class Referral(ReferralBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
