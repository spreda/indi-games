from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

# Подключение логики игры 'Камень-Ножницы-Бумага'
from games.RPS import rps

# Состояния для конечного автомата (FSM)
class RPSStates(StatesGroup):
    playing = State()

# Инициализация роутера для КНБ
router = Router()

# Отправка пользователю клавиатуры с вариантами ходов
async def send_options(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Камень')],
            [KeyboardButton(text='Ножницы')],
            [KeyboardButton(text='Бумага')],
            [KeyboardButton(text='Выход')],
        ],
        resize_keyboard=True,
    )
    await message.answer('Выберите ваш ход:', reply_markup=keyboard)

# Обработчик србытия для начала игры
@router.callback_query((F.data == 'rps_start'))
async def start_game(callback: CallbackQuery, state: FSMContext):
    # Начинаем игру
    await callback.answer() # Отправляем подтверждение нажатия
    await state.set_state(RPSStates.playing)
    await state.update_data(score=0)
    rps.reset_score()  # Сбрасываем счёт игры
    await send_options(callback.message)

# Обработчик сообщения во время игры
@router.message(RPSStates.playing)
async def process_turn(message: Message, state: FSMContext):
    # Нормализуем ввод пользователя
    p_turn = message.text.strip().lower()

    # Проверяем, хочет ли пользователь выйти
    if p_turn == 'выход':
        await exit_game(message, state) 
        return
    
    # Сопоставляем текстовый ввод с внутренними обозначениями игры
    choice_mapping = {
        'камень': 'k',
        'ножницы': 'n',
        'бумага': 'b',
        'к': 'k',
        'н': 'n',
        'б': 'b',
        'k': 'k',
        'n': 'n',
        'b': 'b',
    }

    # Преобразуем ввод пользователя в одно из допустимых значений
    p_turn = choice_mapping.get(p_turn)

    # Проверяем корректность выбора
    if p_turn is None:
        await message.answer('Возможные ходы: Камень, Ножницы, Бумага или Выход')
        return

    # Ход бота
    c_turn = rps.bot_choice()
    winner = rps.determine_winner(p_turn, c_turn)

    # Отправляем результат хода пользователю
    await message.answer(
        f'{rps.knb_choice(c_turn).capitalize()}\n\n'
        f'{winner}\n'
        f'Счет: {rps.count[0]}:{rps.count[1]}'
)

    # Проверка, достиг ли кто-либо из игроков необходимого количества очков
    if 3 in rps.count:
         # Определяем победителя и сообщаем финальный счет
        winner = 'Ты выиграл!' if rps.count[0] == 10 else 'Я выиграл!'
        await message.answer(f'Игра окончена. {winner} Финальный счет - {rps.count[0]}:{rps.count[1]}')
        await exit_game(message, state)
    else:
        # Продолжаем игру, предлагая новые варианты ходов
        await send_options(message)

# Функция для выхода из игры
async def exit_game(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Игра завершена. Выход из игры.', reply_markup=ReplyKeyboardRemove())

# Функция для настройки обработчиков игры
async def setup_game():
    return router  # Возвращаем роутер для подключения к основному приложению