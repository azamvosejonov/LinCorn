from aiogram import executor

from handlers.users.payment import send_payment_reminders
from loader import dp
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)

from aiogram import executor
import asyncio
import logging
from loader import dp, bot, pyment_db, user_db  # Adjust based on your project

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paste the send_payment_reminders function here (as shown above)

async def on_startups(_):
    """Startup function to initialize payment reminders."""
    asyncio.create_task(send_payment_reminders(bot, pyment_db, user_db, interval_seconds=86400.0))
    logger.info("Payment reminder task started.")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startups, skip_updates=True)