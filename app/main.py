from fastapi import FastAPI, HTTPException, status
from .models import User, PaymentVerification, CuratorInfo, Wallet, VerificationResponse
from .database import db
import time
from typing import List
from fastapi.responses import JSONResponse
from fastapi import Query, Body

app = FastAPI(
    title="Pyramid Scheme API",
    description="""
    API for managing a pyramid scheme registration system with the following features:
    * User registration with cryptocurrency wallets (USDT TRC20, BTC, LYC)
    * Referral system (3 referrals required)
    * Curator management
    * Payment verification
    """,
    version="1.0.0"
)

@app.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user with their Telegram ID and cryptocurrency wallets"
)
async def register_user(
    telegram_id: str = Query(..., description="Telegram ID of the user"),
    wallets: List[Wallet] = Body(..., description="List of cryptocurrency wallets")
):
    """
    Register a new user in the system with their Telegram ID and cryptocurrency wallets.
    
    - **telegram_id**: Unique Telegram identifier for the user
    - **wallets**: List of cryptocurrency wallets (USDT TRC20, BTC, LYC)
    """
    if db.get_user(telegram_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    
    if len(wallets) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one wallet is required")
    
    user = User(telegram_id=telegram_id, wallets=wallets)
    return db.create_user(user)

@app.post(
    "/add-referral",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add referral",
    description="Add a referral relationship between two users"
)
async def add_referral(
    referrer_id: str = Query(..., description="Telegram ID of the referrer"),
    referral_id: str = Query(..., description="Telegram ID of the referred user")
):
    """
    Create a referral relationship between two users.
    
    - **referrer_id**: Telegram ID of the referring user
    - **referral_id**: Telegram ID of the user being referred
    """
    referrer = db.get_user(referrer_id)
    if not referrer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referrer not found")
    
    if len(referrer.referrals) >= 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum referrals reached")
    
    referral = db.get_user(referral_id)
    if not referral:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral user not found")
    
    if referral.referrer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has a referrer")
    
    referrer.referrals.append(referral_id)
    referral.referrer_id = referrer_id
    
    if len(referrer.referrals) == 3:
        curator_id = db.get_available_curator([referrer_id] + referrer.referrals)
        if curator_id:
            referrer.curator_id = curator_id
            referrer.curator_contact_visible = True
    
    db.update_user(referrer)
    db.update_user(referral)
    return {"success": True, "message": "Referral added successfully"}

@app.post(
    "/verify-payment",
    response_model=VerificationResponse,
    summary="Verify payment",
    description="Verify payment using a verification code provided by curator"
)
async def verify_payment(
    verification: PaymentVerification = Body(
        ...,
        description="Payment verification details"
    )
):
    """
    Verify a payment using the provided verification code.
    
    - **user_id**: Telegram ID of the user
    - **verification_code**: Unique code provided by the curator
    """
    user = db.get_user(verification.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.curator_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No curator assigned")
    
    curator = db.get_user(user.curator_id)
    if not curator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curator not found")
    
    if verification.verification_code not in user.verification_codes:
        user.verification_codes.append(verification.verification_code)
        db.update_user(user)
    
    remaining_codes = 3 - len(user.verification_codes)
    
    response = VerificationResponse(
        success=True,
        message=f"Code verified. {remaining_codes} more codes needed.",
        remaining_codes=remaining_codes
    )
    
    if remaining_codes == 0:
        response.curator_info = CuratorInfo(
            telegram_id=curator.telegram_id,
            wallets=curator.wallets
        )
    
    return response

@app.post(
    "/request-curator-change",
    response_model=dict,
    summary="Request curator change",
    description="Request a change of curator after 48 hours of inactivity"
)
async def request_curator_change(
    user_id: str = Query(..., description="Telegram ID of the user requesting curator change")
):
    """
    Request a change of curator. There must be a 48-hour waiting period between requests.
    
    - **user_id**: Telegram ID of the user requesting the change
    """
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    current_time = time.time()
    if not user.last_curator_request:
        user.last_curator_request = current_time
        db.update_user(user)
        return {"message": "Curator change requested. Wait 48 hours."}
    
    if current_time - user.last_curator_request < 48 * 3600:
        remaining_time = 48 * 3600 - (current_time - user.last_curator_request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Must wait {remaining_time/3600:.1f} more hours"
        )
    
    new_curator_id = db.get_available_curator([user_id, user.curator_id])
    if not new_curator_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No available curators")
    
    user.curator_id = new_curator_id
    user.last_curator_request = None
    db.update_user(user)
    
    return {"message": "Curator changed successfully"}

@app.get(
    "/user/{telegram_id}",
    response_model=User,
    summary="Get user information",
    description="Get detailed information about a user"
)
async def get_user_info(
    telegram_id: str
):
    """
    Get detailed information about a user.
    
    - **telegram_id**: Telegram ID of the user
    """
    user = db.get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
