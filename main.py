import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from handlers.todo_handler import ToDoBot
from create_bot import dp

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    dp.middleware.setup(LoggingMiddleware())
    todo_bot = ToDoBot(dp)
    executor.start_polling(dp, skip_updates=True)
