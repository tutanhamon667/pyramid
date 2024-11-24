import logging
from typing import Dict, Any, Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import httpx
from datetime import datetime, timedelta

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# States
class UserStates(StatesGroup):
    WALLET_INPUT = State()
    REFERRAL_WAIT = State()
    PAYMENT_VERIFICATION = State()

class PyramidBot:
    def __init__(self, token: str, api_base_url: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.api_base_url = api_base_url
        self._setup_handlers()

    def _setup_handlers(self):
        # Command handlers
        self.dp.message.register(self.start_cmd, Command("start"))
        self.dp.message.register(self.cancel_cmd, Command("cancel"))
        
        # State handlers
        self.dp.message.register(self.process_wallets, UserStates.WALLET_INPUT)
        self.dp.message.register(self.check_referrals, UserStates.REFERRAL_WAIT)
        self.dp.message.register(self.verify_payment, UserStates.PAYMENT_VERIFICATION)
        
        # Callback handlers
        self.dp.callback_query.register(self.handle_curator_change, Text("change_curator"))
        self.dp.callback_query.register(self.check_referrals_callback, Text("check_referrals"))

    async def start_cmd(self, message: types.Message, state: FSMContext) -> None:
        """Start command handler"""
        await state.set_state(UserStates.WALLET_INPUT)
        await message.reply(
            "Welcome to Mavrodi's Tears Pyramid! \n\n"
            "Our rules are simple:\n"
            "- Only 100 keys available\n"
            "- Each key costs 2x more than the previous one\n"
            "- First key costs $1\n"
            "- No commissions taken by organizers\n"
            "- You must bring at least 3 people and receive payment from them\n\n"
            "Please enter your wallet addresses in the following format:\n"
            "USDT TRC20: <address>\n"
            "BTC: <address>\n"
            "LYC: <address>"
        )

    async def cancel_cmd(self, message: types.Message, state: FSMContext) -> None:
        """Cancel command handler"""
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()
        await message.reply("Operation cancelled. Type /start to begin again.")

    async def process_wallets(self, message: types.Message, state: FSMContext) -> None:
        """Process wallet addresses"""
        try:
            wallet_text = message.text
            wallets = []
            
            for line in wallet_text.split('\n'):
                if 'USDT TRC20:' in line:
                    wallets.append({"type": "USDT_TRC20", "address": line.split(':')[1].strip()})
                elif 'BTC:' in line:
                    wallets.append({"type": "BTC", "address": line.split(':')[1].strip()})
                elif 'LYC:' in line:
                    wallets.append({"type": "LYC", "address": line.split(':')[1].strip()})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/register",
                    params={"telegram_id": str(message.from_user.id)},
                    json=wallets
                )
                
                if response.status_code == 201:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Check Referrals", callback_data="check_referrals")]
                    ])
                    
                    await state.set_state(UserStates.REFERRAL_WAIT)
                    await message.reply(
                        "Registration successful! \n"
                        "You need to bring 3 people to proceed.\n"
                        f"Share your Telegram ID with them: {message.from_user.id}\n\n"
                        "Click 'Check Referrals' to see your progress.",
                        reply_markup=keyboard
                    )
                else:
                    await message.reply(" Registration failed. Please try again or contact support.")
                    await state.clear()

        except Exception as e:
            logger.error(f"Error in process_wallets: {e}")
            await message.reply(
                " Invalid wallet format. Please try again with the correct format:\n"
                "USDT TRC20: <address>\n"
                "BTC: <address>\n"
                "LYC: <address>"
            )

    async def check_referrals(self, message: types.Message, state: FSMContext) -> None:
        """Check referral status"""
        await self._check_referrals_impl(message.from_user.id, message)

    async def check_referrals_callback(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        """Handle check referrals button click"""
        await callback_query.answer()
        await self._check_referrals_impl(callback_query.from_user.id, callback_query.message)

    async def _check_referrals_impl(self, user_id: int, message_obj: types.Message) -> None:
        """Implementation of referral checking logic"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base_url}/user/{user_id}")
            
            if response.status_code == 200:
                user_data = response.json()
                referral_count = len(user_data.get("referrals", []))
                
                if referral_count >= 3:
                    curator_data = user_data.get("curator", {})
                    await message_obj.reply(
                        f" Congratulations! You have {referral_count} referrals.\n\n"
                        f"Your curator contact: @{curator_data.get('telegram_id')}\n"
                        "Please contact your curator for payment instructions and verification code.\n"
                        "Enter the verification code when received:"
                    )
                    await state.set_state(UserStates.PAYMENT_VERIFICATION)
                else:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Check Referrals", callback_data="check_referrals")]
                    ])
                    await message_obj.reply(
                        f"You currently have {referral_count}/3 referrals.\n"
                        "Keep sharing your Telegram ID to get more referrals!",
                        reply_markup=keyboard
                    )

    async def verify_payment(self, message: types.Message, state: FSMContext) -> None:
        """Verify payment code"""
        verification_code = message.text.strip()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/verify-payment",
                json={
                    "user_id": str(message.from_user.id),
                    "verification_code": verification_code
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                remaining_codes = data.get("remaining_codes", 0)
                
                if remaining_codes > 0:
                    await message.reply(f" Payment verified! You need {remaining_codes} more verification codes.")
                else:
                    next_curator = data.get("next_curator", {})
                    await message.reply(
                        " All payments verified!\n\n"
                        f"Next curator contact: @{next_curator.get('telegram_id')}\n"
                        "Wallet addresses:\n" +
                        "\n".join([f"{w['type']}: {w['address']}" for w in next_curator.get("wallets", [])])
                    )
                    await state.clear()
            else:
                await message.reply(" Invalid verification code. Please contact your curator for the correct code.")

    async def handle_curator_change(self, callback_query: types.CallbackQuery) -> None:
        """Handle curator change request"""
        await callback_query.answer()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/request-curator-change",
                params={"user_id": str(callback_query.from_user.id)}
            )
            
            if response.status_code == 200:
                await callback_query.message.edit_text(
                    " Curator change requested. Please wait 48 hours for the change to take effect."
                )
            else:
                await callback_query.answer(
                    " Cannot request curator change at this time.",
                    show_alert=True
                )

    async def start(self):
        """Start the bot"""
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()