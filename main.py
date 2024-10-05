import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import KeyboardButton, WebAppInfo, CallbackQuery

# Токен бота можно получить через https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
WEB_APP_URL = getenv("WEB_APP_URL")

# Все обработчики должны быть подключены к диспетчеру
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: Message) -> None:
    """
    Обработчик для команды /start
    Показывает приветственное сообщение с выбором игр.
    """
    # Создание кнопок для выбора игр    
    snake = InlineKeyboardButton(text="Змейка", web_app=WebAppInfo(url=f"{WEB_APP_URL}"))
    sea_battle = InlineKeyboardButton(text="Морской бой", callback_data="sea_battle")
    rock_paper_scissors = InlineKeyboardButton(text="Камень ножницы бумага", callback_data="rock_paper_scissors")

    # Создание разметки клавиатуры и добавление кнопок
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[snake], [sea_battle], [rock_paper_scissors]])

    # Отправка приветственного сообщения с клавиатурой
    await message.answer(f"Добро пожаловать, {message.from_user.full_name}! Выберите игру:", reply_markup=keyboard)


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Обработчик для любых сообщений, который пересылает отправленное сообщение обратно.
    """
    try:
        # Отправка копии полученного сообщения обратно отправителю
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # Обработка типов сообщений, которые не поддерживаются для копирования
        await message.answer("Хорошая попытка!")


@dp.callback_query()
async def process_callback_button1(callback_query: CallbackQuery):
    """
    Обработчик для нажатий на кнопки клавиатуры.
    """
    await callback_query.answer()
    await callback_query.message.answer(text=f'{callback_query.data} [Placeholder]')

async def main() -> None:
    # Инициализация экземпляра бота с настройками по умолчанию
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Запуск диспетчера для обработки событий
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())