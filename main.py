from aiogram.utils import executor
from commands import dispatcher

async def on_bot_start(_):
    print('bot is started')

if __name__ == '__main__':
    executor.start_polling(dispatcher, on_startup=on_bot_start)