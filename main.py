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
from games.RPS import rps_adapter

# Получаем токен бота и URL веб-приложения из переменных окружения
TOKEN = getenv('BOT_TOKEN')
WEB_APP_URL = getenv('WEB_APP_URL')

# Инициализируем хранилище состояний в памяти
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def send_menu(message: Message):
    """
    Функция отправки сообщения со списком игр. 
    """    
    snake = InlineKeyboardButton(text='Змейка', web_app=WebAppInfo(url=f'{WEB_APP_URL}/games/Snake/snake.html'))
    battleship = InlineKeyboardButton(text='Морской бой', callback_data='battleship')
    rps = InlineKeyboardButton(text='Камень ножницы бумага', callback_data='rps_start')

    # Формируем разметку с кнопками для выбора игры
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[snake], [battleship], [rps]])

    await message.answer(text='Выберите игру:', reply_markup=keyboard)

@dp.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    """
    Обработчик для команды /start
    Очищает текущее состояние пользователя.
    Показывает приветственное сообщение с выбором игр.
    """
    await state.clear()
    await message.answer(text=f'Добро пожаловать, {message.from_user.full_name}!', reply_markup=ReplyKeyboardRemove())
    await send_menu(message)

@dp.callback_query(F.data == 'battleship')
async def process_menu_callback(callback_query: CallbackQuery):
    """
    Обработчик для кнопки "Морской бой"
    """
    await callback_query.answer()
    message = callback_query.message
    data = callback_query.data
    await message.answer(text=f'{data} [Placeholder]')

async def main():
    """
    Основная точка входа в приложение. 
    Инициализирует бота и диспетчер, подключает маршруты и запускает опрос событий.
    """
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Подключаем маршруты игры "Камень-Ножницы-Бумага"
    rps_router = await rps_adapter.setup_game()
    dp.include_router(rps_router)

    # Запускаем диспетчер для обработки событий
    await dp.start_polling(bot)

@dp.message(Command('state'))
async def print_state(message: Message, state: FSMContext):
    """
    Команда /state.
    Показывает текущее состояние конечного автомата (FSM) для отладки.
    """
    state = await state.get_state()
    await message.answer(text=f'{state}')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main()) # Запуск основного цикла программы
