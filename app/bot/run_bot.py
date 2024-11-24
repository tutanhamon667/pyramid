import os
import asyncio
from dotenv import load_dotenv
from bot import PyramidBot

# Load environment variables
load_dotenv()

async def main():
    # Get configuration from environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    # Create and run the bot
    bot = PyramidBot(token=token, api_base_url=api_base_url)
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())