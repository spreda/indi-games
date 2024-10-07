from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

# Assuming rps.py is in the games/rps directory
from games.rps import rps

# Состояния чата пользователя
class RPSStates(StatesGroup):
    playing = State()

# Define a callback data factory for RPS
class RPSCallbackData(CallbackData, prefix="rps_"):
    action: str

# The router for RPS
router = Router()

async def send_options(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Камень")],
            [KeyboardButton(text="Ножницы")],
            [KeyboardButton(text="Бумага")],
            [KeyboardButton(text="Выход")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите ваш ход:", reply_markup=keyboard)

@router.callback_query((F.data == "rps_start"))
async def start_game(callback: CallbackQuery, state: FSMContext):
    print('starting rps')
    await callback.answer()
    await state.set_state(RPSStates.playing)
    await state.update_data(score=0)
    print('state:', await state.get_state(), 'data:', await state.get_data())
    rps.reset_score()  # Reset score for new game
    await send_options(callback.message)

@router.message(RPSStates.playing)
async def process_turn(message: Message, state: FSMContext):
    # Normalize input
    p_turn = message.text.strip().lower()

    # Check if the user wants to exit
    if p_turn == "выход":
        await exit_game(message, state) 
        return
    
    # Define mapping for movements
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

    p_turn = choice_mapping.get(p_turn)

    # Validate the choice
    if p_turn is None:
        await message.answer('Возможные ходы: Камень, Ножницы, Бумага или Выход')
        return


    c_turn = rps.bot_choice()
    winner = rps.determine_winner(p_turn, c_turn)

    await message.answer(
f'''
{rps.knb_choice(p_turn)} vs {rps.knb_choice(c_turn)}
{winner}
Счет: {rps.count[0]}:{rps.count[1]}
''')

    if 10 in rps.count:
        winner = "Ты выиграл!" if rps.count[0] == 10 else "Я выиграл!"
        await message.answer(f"Игра окончена. {winner} Финальный счет - {rps.count[0]}:{rps.count[1]}")
        await exit_game(message, state)
    else:
        await send_options(message)

async def exit_game(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Игра завершена. Выход из игры.', reply_markup=ReplyKeyboardRemove())

# Function to set up RPS handlers
async def setup_game():
    return router  # Returning the router for inclusion in the application