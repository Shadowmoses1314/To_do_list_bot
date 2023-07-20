from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from data_base.sql_db import Database

db = Database('todo.db')


class TaskCreation(StatesGroup):
    title = State()
    text = State()


class ToDoBot:
    def __init__(self, dp):
        self.dp = dp
        self.register_handlers()

    def register_handlers(self):
        self.dp.register_message_handler(self.on_start, commands=['start'])
        self.dp.register_message_handler(self.on_add,
                                         commands=['add', 'Добавить_задачу'],
                                         state="*")
        self.dp.register_message_handler(self.on_cancel,
                                         commands=['cancel', 'Отмена_создания'],
                                         state="*")
        self.dp.register_message_handler(self.load_title,
                                         state=TaskCreation.title)
        self.dp.register_message_handler(self.load_text,
                                         state=TaskCreation.text)
        self.dp.register_message_handler(self.on_done, commands=['done'])
        self.dp.register_message_handler(self.on_list,
                                         commands=['list', 'Все_задачи'])
        self.dp.register_message_handler(self.on_delete, commands=['delete'])
        self.dp.register_callback_query_handler(self.on_callback_query)

    async def on_start(self, message: types.Message):
        await message.answer(
            "Привет! Я твой личный помощник по управлению задачами.\n"
            "Используй меню чтобы добавить и посмотреть задачи\n"
            "Чтобы отметить задачу выполненной, используй команду: /done <индекс>\n"
            "Чтобы посмотреть список задач, используй команду: /list\n"
            "Чтобы удалить задачу из списка, используй команду: /delete <индекс>\n"
        )

    async def on_add(self, message: types.Message):
        await TaskCreation.title.set()
        await message.reply("Введите заголовок задачи:")

    async def on_cancel(self, message: types.Message, state: FSMContext):
        await state.finish()
        await message.reply("Создание задачи отменено.")

    async def load_title(self, message: types.Message, state: FSMContext):
        title = message.text
        await state.update_data(title=title)
        await TaskCreation.text.set()
        await message.reply("Введите описание задачи:")

    async def load_text(self, message: types.Message, state: FSMContext):
        text = message.text
        data = await state.get_data()
        title = data.get('title')
        db.add_task(title, text)
        await state.finish()
        await message.reply(f"Задача '{title}: {text}' добавлена.")

    async def on_delete(self, message: types.Message, task_id: int):
        if db.delete_task(task_id):
            await message.reply(f"Задача с ID {task_id} удалена.")
        else:
            await message.reply(f"Задача с ID {task_id} не найдена.")

    async def on_done(self, message: types.Message, task_id: int):
        if db.mark_task_done(task_id):
            await message.reply(
                f"Задача с ID {task_id} отмечена как выполненная."
                )
        else:
            await message.reply(f"Задача с ID {task_id} не найдена.")

    async def on_list(self, message: types.Message):
        tasks = db.get_all_tasks()
        if not tasks:
            await message.reply("Список задач пуст.")
            return

        for task in tasks:
            task_text = (
                f"Задача №{task['id']}\n"
                f"Статус выполнения: {'✓' if task['done'] else '✘'}\n"
                f"Заголовок: {task['title']}\n"
                f"Описание: {task['text']}\n"
            )

            inline_keyboard = InlineKeyboardMarkup(row_width=2)
            delete_button = InlineKeyboardButton(
                "Удалить",
                callback_data=f"/delete,{task['id']}"
                )
            done_button = InlineKeyboardButton(
                "Выполнить задачу",
                callback_data=f"/done,{task['id']}")
            inline_keyboard.add(delete_button, done_button)

            await message.reply(task_text, reply_markup=inline_keyboard)

    async def on_callback_query(self, query: types.CallbackQuery):
        action, task_id = query.data.split(',')
        task_id = int(task_id)

        if action == '/delete':
            await self.on_delete(query.message, task_id)
        elif action == '/done':
            await self.on_done(query.message, task_id)
        else:
            await query.answer("Unknown action")
