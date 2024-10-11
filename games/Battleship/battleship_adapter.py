from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Подключение логики игры 'Морской бой'
from games.Battleship.battleship import BattleshipSession

# Состояния для конечного автомата (FSM)
class BattleshipStates(StatesGroup):
    setup = State()
    playing = State()
    waiting = State()

# Хранение игровых сессий
waiting_queue: list[Message] = list()
sessions: dict[int, tuple[int, BattleshipSession]] = dict()

def get_session(message: Message) -> BattleshipSession:
    return sessions.get(message.from_user.id)

# Инициализация роутера для Морского боя
router = Router()

# Отправка пользователю клавиатуры с вариантами ходов
async def send_turn_options(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=list([KeyboardButton(text=f'{x}, {y}') for x in range(5)] for y in range(5)),
        resize_keyboard=True,
    )
    session = get_session(message)
    await message.answer(
        text= '\n\n'.join((
            f'Ход {session.current_player.name}:',
            f'{session.opponent.render_board()}',
            f'{session.current_player.render_board()}',
            'Выберите ваш ход:'
        )),
        reply_markup=keyboard
    )

# Обработчик србытия для начала игры
@router.callback_query((F.data == 'battleship_start'))
async def start_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer() # Отправляем подтверждение нажатия
    await state.set_state(BattleshipStates.setup)
    await callback.message.answer('Setup...')
    await setup_session(callback.message, state)

# Обработчик сообщения во время настройки игры
@router.message(BattleshipStates.setup)
async def setup_session(message: Message, state: FSMContext):
    if waiting_queue:
        player_1 = message.from_user
        player_2 = waiting_queue.pop().from_user
        player1_name = player_1.full_name
        player2_name = player_2.full_name 
        id_1 = player_1.id
        id_2 = player_2.id
        sessions[id_1] = BattleshipSession(player1_name, player2_name, 5, {4: 0, 2: 1, 1: 3})
        sessions[id_2] = sessions[id_1]
        print(f'Create session: {sessions[id_1]}.\nIDs: {id_1}, {id_2}')
        await state.set_state(BattleshipStates.playing)
        await send_turn_options(message)
    else:
        waiting_queue.append(message)
        await state.set_state(BattleshipStates.waiting)
        await message.answer('Ожидание игроков...')

@router.message(Command('sessions'))
async def print_sessions(message: Message):
    await message.answer(f'{sessions}')

@router.message(Command('test'))
async def print_sessions(message: Message, state: FSMContext):
    await setup_session(message, state)

@router.message(BattleshipStates.waiting)
async def wait_turn(message: Message):
    message.answer(f'Ожидание хода игрока {get_session(message).current_player}')

# Обработчик сообщения во время игры
@router.message(BattleshipStates.playing)
async def process_turn(message: Message, state: FSMContext):
    # Нормализуем ввод пользователя
    p_turn = message.text.strip().lower()

    # Проверяем, хочет ли пользователь выйти
    if p_turn == 'выход':
        await exit_game(message, state) 
        return
    
    # Сопоставляем текстовый ввод с внутренними обозначениями игры
    x, y = p_turn.split(', ')

    # Валидация ввода пользователя
    session = get_session(message)
    error = session.validate_input(x, y)
    if error:
        message.answer(text=error)
        await send_turn_options(message)
        return

    # Обработка хода
    hit, hit_text = session.process_turn(x, y)

    # Отправляем результат хода пользователю
    await message.answer(hit_text)

    # Проверка, достиг ли кто-либо из игроков необходимого количества очков
    if session.is_game_over():
         # Определяем победителя и сообщаем финальный счет
        winner = session.current_player.name
        await message.answer(f'Игра окончена. Победил {winner}')
        await exit_game(message, state)
    else:
        # Продолжаем игру, предлагая новые варианты ходов
        await send_turn_options(message)

# Функция для выхода из игры
async def exit_game(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Игра завершена. Выход из игры.', reply_markup=ReplyKeyboardRemove())

# Функция для настройки обработчиков игры
async def setup_game():
    return router  # Возвращаем роутер для подключения к основному приложению





