from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .database import Base
import enum

class WalletType(str, enum.Enum):
    USDT_TRC20 = "USDT_TRC20"
    BTC = "BTC"
    LYC = "LYC"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    referrer_id = Column(String, nullable=True)
    curator_id = Column(String, nullable=True)
    key_number = Column(Integer, nullable=True)
    curator_contact_visible = Column(Boolean, default=False)
    last_curator_request = Column(Float, nullable=True)
    verification_codes = Column(ARRAY(String), default=list)

    # Relationships
    wallets = relationship("Wallet", back_populates="user")
    referrals = relationship(
        "User",
        secondary="referral_relationships",
        primaryjoin="User.telegram_id==ReferralRelationship.referrer_id",
        secondaryjoin="User.telegram_id==ReferralRelationship.referral_id",
        backref="referrer"
    )

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(SQLEnum(WalletType))
    address = Column(String)

    # Relationship
    user = relationship("User", back_populates="wallets")

class ReferralRelationship(Base):
    __tablename__ = "referral_relationships"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(String, ForeignKey("users.telegram_id"))
    referral_id = Column(String, ForeignKey("users.telegram_id"))

class Key(Base):
    __tablename__ = "keys"

    number = Column(Integer, primary_key=True)
    price = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
