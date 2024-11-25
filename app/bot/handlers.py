from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import SessionLocal
from app.db.schemas import UserCreate, WalletCreate

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"Hi {user.first_name}! 👋\n\n"
        "Welcome to the Pyramid Marketing Bot. Here's what you can do:\n\n"
        "🔹 /register - Create your account\n"
        "🔹 /wallet - Set up your crypto wallet\n"
        "🔹 /referral - Get your referral link\n"
        "🔹 /help - Show this help message\n\n"
        "Let's get started! 🚀"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Here are the available commands:\n\n"
        "🔹 /register - Create your account\n"
        "🔹 /wallet - Set up your crypto wallet\n"
        "🔹 /referral - Get your referral link\n"
        "🔹 /help - Show this help message\n\n"
        "Need assistance? Contact our support."
    )
    await update.message.reply_text(help_text)

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register a new user."""
    user = update.effective_user
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = crud.get_user_by_telegram_id(db, user.id)
        if existing_user:
            await update.message.reply_text("You're already registered! 😊")
            return

        # Create new user
        new_user = UserCreate(
            telegram_id=user.id,
            username=user.username,
            full_name=user.full_name
        )
        crud.create_user(db, new_user)
        await update.message.reply_text(
            "Registration successful! 🎉\n"
            "Use /wallet to set up your crypto wallet."
        )
    finally:
        db.close()

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle wallet setup."""
    user = update.effective_user
    db = SessionLocal()
    try:
        db_user = crud.get_user_by_telegram_id(db, user.id)
        if not db_user:
            await update.message.reply_text(
                "Please /register first before setting up your wallet."
            )
            return

        # Check if wallet already exists
        existing_wallet = crud.get_user_wallet(db, db_user.id)
        if existing_wallet:
            wallet_info = (
                "Your wallet addresses:\n\n"
                f"BTC: {existing_wallet.btc_address or 'Not set'}\n"
                f"USDT: {existing_wallet.usdt_address or 'Not set'}\n"
                f"LYC: {existing_wallet.lyc_address or 'Not set'}"
            )
            await update.message.reply_text(wallet_info)
            return

        # Start wallet setup conversation
        await update.message.reply_text(
            "Let's set up your wallet! 💼\n"
            "Please send your wallet addresses in the following format:\n\n"
            "BTC: your_btc_address\n"
            "USDT: your_usdt_address\n"
            "LYC: your_lyc_address"
        )
    finally:
        db.close()

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle referral link generation."""
    user = update.effective_user
    db = SessionLocal()
    try:
        db_user = crud.get_user_by_telegram_id(db, user.id)
        if not db_user:
            await update.message.reply_text(
                "Please /register first to get your referral link."
            )
            return

        # Get user's referrals
        referrals = crud.get_user_referrals(db, db_user.id)
        referral_link = f"https://t.me/PyramidMarketingBot?start={db_user.id}"
        
        response = (
            f"🔗 Your referral link: {referral_link}\n\n"
            f"👥 Total referrals: {len(referrals)}\n\n"
            "Share this link with your friends and earn rewards! 💰"
        )
        await update.message.reply_text(response)
    finally:
        db.close()
