"""
Pyramid Marketing Bot - A Telegram-based MLM platform with cryptocurrency payments.
"""

__version__ = "1.0.0"

from .main import app
from .models import User, Wallet, PaymentVerification, CuratorInfo, VerificationResponse
from .database import db

__all__ = ['app', 'User', 'Wallet', 'PaymentVerification', 'CuratorInfo', 'VerificationResponse', 'db']
