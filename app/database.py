from typing import Dict, Optional
from .models import User
import random
import string

class MockDatabase:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.current_key = 1
        self.key_prices = {1: 1.0}  # Initialize first key price
        self._initialize_key_prices()

    def _initialize_key_prices(self):
        # Initialize prices for all 100 keys
        for i in range(2, 101):
            self.key_prices[i] = self.key_prices[i-1] * 2

    def get_user(self, telegram_id: str) -> Optional[User]:
        return self.users.get(telegram_id)

    def create_user(self, user: User) -> User:
        if user.telegram_id not in self.users:
            user.key_number = self.current_key
            self.users[user.telegram_id] = user
            self.current_key += 1
        return self.users[user.telegram_id]

    def update_user(self, user: User) -> User:
        self.users[user.telegram_id] = user
        return user

    def generate_verification_code(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def get_key_price(self, key_number: int) -> float:
        return self.key_prices.get(key_number, float('inf'))

    def get_available_curator(self, exclude_ids: list[str]) -> Optional[str]:
        # Mock implementation - in real system, this would be more sophisticated
        for user_id, user in self.users.items():
            if (user_id not in exclude_ids and 
                len(user.referrals) >= 3 and 
                len([u for u in self.users.values() if u.curator_id == user_id]) < 3):
                return user_id
        return None

# Global database instance
db = MockDatabase()
