from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


b1 = KeyboardButton('/Добавить_задачу')
b2 = KeyboardButton('/Все_задачи')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

KeyboardClient = kb_client.add(b1).row(b2)
