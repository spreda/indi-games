import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.types import KeyboardButton, WebAppInfo, CallbackQuery
from games.rps import rps_adapter

# Токен бота можно получить через https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
WEB_APP_URL = getenv("WEB_APP_URL")

# Все обработчики должны быть подключены к диспетчеру
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def send_menu(message: Message):
    # Создание кнопок для выбора игр    
    snake = InlineKeyboardButton(text="Змейка", web_app=WebAppInfo(url=f"{WEB_APP_URL}/games/Snake/snake.html"))
    sea_battle = InlineKeyboardButton(text="Морской бой", callback_data="sea_battle")
    rps = InlineKeyboardButton(text="Камень ножницы бумага", callback_data="rps_start")

    # Создание разметки клавиатуры и добавление кнопок
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[snake], [sea_battle], [rps]])

    # Отправка приветственного сообщения с клавиатурой
    await message.answer(text=f'Добро пожаловать, {message.from_user.full_name}!', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Выберите игру:', reply_markup=keyboard)

@dp.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    """
    Обработчик для команды /start
    Показывает приветственное сообщение с выбором игр.
    """
    await state.clear()
    await send_menu(message)

@dp.callback_query(F.data == 'sea_battle')
async def process_menu_callback(callback_query: CallbackQuery):
    """
    Обработчик для нажатий на кнопки клавиатуры.
    """
    await callback_query.answer()
    message = callback_query.message
    data = callback_query.data
    await message.answer(text=f'{data} [Placeholder]')

async def main() -> None:
    # Инициализация экземпляра бота с настройками по умолчанию
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Initialize and set up the Rock-Paper-Scissors (RPS) game router
    rps_router = await rps_adapter.setup_game()

    # Include the RPS router in the dispatcher
    dp.include_router(rps_router)

    # Запуск диспетчера для обработки событий
    await dp.start_polling(bot)

@dp.message(Command('state'))
async def print_state(message: Message, state: FSMContext):
    state = await state.get_state()
    await message.answer(text=f'{state}')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())