from aiogram import Router, F
from aiogram.fsm.storage.base import StorageKey
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


class Player:
    def __init__(self, message:Message):
        self.name = message.from_user.full_name
        self.id = message.from_user.id
        self.chat_id = message.chat.id
        self.bot = message.bot

    async def answer(self, **kwargs):
        await self.bot.send_message(chat_id=self.chat_id, **kwargs)
        
    def get_storage_key(self):
        return StorageKey(self.bot.id, self.chat_id, self.id)
    
    def get_context(self):
        return FSMContext(storage=storage, key=self.get_storage_key())


class GameSession:
    def __init__(self, state:BattleshipSession, player_1:Player, player_2:Player):
        self.state = state
        self.player_1 = player_1
        self.player_2 = player_2
        self.__player_name_mappping ={
            self.player_1.name: player_1,
            self.player_2.name: player_2,
        }
    
    def get_current_player(self):
        return self.__player_name_mappping.get(self.state.current_player.name)
    
    def get_opponent(self):
        return self.__player_name_mappping.get(self.state.opponent.name)
    
    async def answer_everyone(self, **kwargs):
        await self.player_1.answer(**kwargs)
        await self.player_2.answer(**kwargs)


# Хранение игровых сессий
storage = None
waiting_queue: list[Player] = list()
sessions: dict[int, GameSession] = dict()

def get_session(message: Message) -> GameSession:
    return sessions.get(message.from_user.id)

# Инициализация роутера для Морского боя
router = Router()

# Отправка пользователю клавиатуры с вариантами ходов
async def send_turn_options(player: Player):
    if await player.get_context().get_state() != BattleshipStates.playing:
        await player.answer(text='Ошибка, дождитесь своего хода')
        return
    
    letters = 'АБВГДЕЖЗИК'
    keyboard = ReplyKeyboardMarkup(
        keyboard=list([KeyboardButton(text=f'{letters[x]}{y+1}') for x in range(5)] for y in range(5)) + [[KeyboardButton(text='Выход')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await player.answer(
        text=('Выберите ваш ход:'),
        reply_markup=keyboard
    )

# Обработчик србытия для начала игры
@router.callback_query((F.data == 'battleship_start'))
async def start_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer() # Отправляем подтверждение нажатия
    await state.set_state(BattleshipStates.setup)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Старт')]],
        resize_keyboard=True,
    )
    await callback.message.answer(text='Setup...', reply_markup=keyboard)

# Обработчик сообщения во время настройки игры
@router.message(BattleshipStates.setup)
async def setup_session(message: Message, state: FSMContext):
    player_1 = message.from_user
    if waiting_queue:
        player_2 = waiting_queue.pop()
        player_1 = Player(message=message)
        sessions[player_1.chat_id] = GameSession(
            BattleshipSession(player_1.name, player_2.name, 5, {4: 0, 2: 1, 1: 3}),
            player_1,
            player_2
        )
        sessions[player_2.chat_id] = sessions[player_1.chat_id]
        print(f'Create session: {sessions[player_1.chat_id]}.\nIDs: {player_1.chat_id}, {player_2.chat_id}')
        await state.set_state(BattleshipStates.playing)
        await send_turn_options(player_1)
        await player_2.answer(text=f'Ожидание хода {player_1.name}')
    else:
        waiting_queue.append(Player(message=message))
        await state.set_state(BattleshipStates.waiting)
        await message.answer(f'Ожидание игроков...')

@router.message(BattleshipStates.waiting)
async def wait_turn(message: Message):
    await message.answer(f'Ожидание хода {get_session(message).state.current_player.name}')

# Обработчик сообщения во время игры
@router.message(BattleshipStates.playing)
async def process_turn(message: Message, state: FSMContext):
    session = get_session(message)
    current_player = session.get_current_player()
    opponent = session.get_opponent()
    # Нормализуем ввод пользователя
    p_turn = message.text.strip().lower()

    # Проверяем, хочет ли пользователь выйти
    if p_turn == 'выход':
        await exit_game(message, state) 
        return
    
    # Сопоставляем текстовый ввод с внутренними обозначениями игры
    x, y = p_turn[:2]
    x = ord(x) - ord('а')
    y = int(y) - 1

    # Валидация ввода пользователя
    error = session.state.validate_input(x, y)
    if error:
        await message.answer(text=error)
        await send_turn_options(current_player)
        return

    # Обработка хода
    print(state.get_state, opponent.get_context().get_state)
    await state.set_state(BattleshipStates.waiting)
    await opponent.get_context().set_state(BattleshipStates.playing)
    hit, hit_text = session.state.process_turn(x, y)

    # Отправляем результат хода пользователю
    result = f'{hit_text}\n{session.state.board_1.render_board()}\n\n{session.state.board_2.render_board()}'
    await session.answer_everyone(text=result)

    # Проверка, достиг ли кто-либо из игроков необходимого количества очков
    if session.state.is_game_over():
         # Определяем победителя и сообщаем финальный счет
        winner = current_player
        await session.answer_everyone(f'Игра окончена. Победил {winner.name}')
        await exit_game(message)
    else:
        # Продолжаем игру, предлагая новые варианты ходов
        await send_turn_options(opponent)

# Функция для выхода из игры
async def exit_game(message: Message):
    session = get_session(message)
    await session.player_1.get_context().clear()
    await session.player_2.get_context().clear()
    await session.answer_everyone('Игра завершена. Выход из игры.', reply_markup=ReplyKeyboardRemove())

# Функция для настройки обработчиков игры
async def setup_game(storage_):
    global storage
    storage = storage_
    return router  # Возвращаем роутер для подключения к основному приложению
