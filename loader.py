from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils.db_api.student_db import StudentDatabase
from utils.db_api.jadval_db import JadvalDatabase
from utils.db_api.admin_db import AdminDatabase
from utils.db_api.pyment_db import PymentDatabase

from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_db = StudentDatabase(db_path="data/main.db", bot=bot)
jadval_db=JadvalDatabase(path_to_db="data/main.db")
admin_db=AdminDatabase(path_to_db="data/main.db")
pyment_db=PymentDatabase(path_to_db="data/main.db")

