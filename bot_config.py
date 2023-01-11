from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

bot = Bot(token = '5828344959:AAFGi6JBz13yHR3aCm5FJlyts7EKvrlpbTo')
dispatcher = Dispatcher(bot, storage=storage)