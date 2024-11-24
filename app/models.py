from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class WalletType(str, Enum):
    USDT_TRC20 = "USDT_TRC20"
    BTC = "BTC"
    LYC = "LYC"

class Wallet(BaseModel):
    type: WalletType = Field(..., description="Type of cryptocurrency wallet")
    address: str = Field(..., description="Wallet address", example="TRC20123456789")

    class Config:
        schema_extra = {
            "example": {
                "type": "USDT_TRC20",
                "address": "TRC20123456789"
            }
        }

class User(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID of the user", example="user123")
    wallets: List[Wallet] = Field(..., description="List of cryptocurrency wallets")
    referrer_id: Optional[str] = Field(None, description="Telegram ID of the referrer")
    referrals: List[str] = Field(default_factory=list, description="List of referral Telegram IDs")
    curator_id: Optional[str] = Field(None, description="Telegram ID of the curator")
    key_number: Optional[int] = Field(None, description="Assigned key number (1-100)")
    verification_codes: List[str] = Field(default_factory=list, description="List of verified payment codes")
    curator_contact_visible: bool = Field(False, description="Whether curator contact is visible")
    last_curator_request: Optional[float] = Field(None, description="Timestamp of last curator change request")

    class Config:
        schema_extra = {
            "example": {
                "telegram_id": "user123",
                "wallets": [
                    {
                        "type": "USDT_TRC20",
                        "address": "TRC20123456789"
                    },
                    {
                        "type": "BTC",
                        "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
                    }
                ],
                "referrer_id": None,
                "referrals": [],
                "curator_id": None,
                "key_number": 1,
                "verification_codes": [],
                "curator_contact_visible": False,
                "last_curator_request": None
            }
        }

class PaymentVerification(BaseModel):
    user_id: str = Field(..., description="Telegram ID of the user", example="user123")
    verification_code: str = Field(..., description="Verification code provided by curator", example="ABC123")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "verification_code": "ABC123"
            }
        }

class CuratorInfo(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID of the curator", example="curator123")
    wallets: List[Wallet] = Field(..., description="List of curator's cryptocurrency wallets")

    class Config:
        schema_extra = {
            "example": {
                "telegram_id": "curator123",
                "wallets": [
                    {
                        "type": "USDT_TRC20",
                        "address": "TRC20987654321"
                    }
                ]
            }
        }

class VerificationResponse(BaseModel):
    success: bool = Field(..., description="Whether the verification was successful")
    message: str = Field(..., description="Response message")
    remaining_codes: Optional[int] = Field(None, description="Number of remaining codes needed")
    curator_info: Optional[CuratorInfo] = Field(None, description="Curator information if all codes are verified")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Code verified. 2 more codes needed.",
                "remaining_codes": 2,
                "curator_info": None
            }
        }
