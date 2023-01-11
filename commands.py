from bot_config import dispatcher, bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
import aiogram.utils.markdown as md
from candies_game import CandiesGameState
import candies_game
import emoji
import random

async def user_makes_turn_and_update_state(user_took_candies_count:int, state: FSMContext):
    await state.update_data(player_one_last_candies_getted=user_took_candies_count)
    newState = candies_game.reduce_candies(
        CandiesGameState.player_one_candies_count, 
        CandiesGameState.candies_left, 
        CandiesGameState.max_candies_count_to_take, 
        lambda _, __: user_took_candies_count)

    CandiesGameState.is_game_finished = newState[0]
    CandiesGameState.player_one_candies_count = newState[1]
    CandiesGameState.candies_left = newState[2]

def bot_makes_turn_and_update_state():
    newState = candies_game.reduce_candies(
        CandiesGameState.player_two_candies_count, 
        CandiesGameState.candies_left, 
        CandiesGameState.max_candies_count_to_take, 
        candies_game.calculate_candies_to_take)

    CandiesGameState.is_game_finished = newState[0]
    CandiesGameState.player_two_candies_count = newState[1]
    CandiesGameState.candies_left = newState[2]
    CandiesGameState.player_two_last_candies_getted = newState[3]

async def drop_state(state: FSMContext):
    CandiesGameState.candies_left = 150
    CandiesGameState.max_candies_count_to_take = 28

    CandiesGameState.player_one_candies_count = 0
    CandiesGameState.player_two_candies_count = 0

    CandiesGameState.is_game_finished = False
    CandiesGameState.player_two_last_candies_getted = 0

    await state.finish()

async def send_win_message(userid: int, who_win_game:str):
    return await bot.send_message(userid, text=f"Игра окончена. {who_win_game} победил")

async def send_invalid_candies_count_message(userid: int, max_count:int):
    return await bot.send_message(userid, text=f"количество конфет должно быть числом.\nВведи число от 1 до {max_count} мой юный падаван (вводить только цифры)")

async def send_update_state_message(userid:int, username:str, last_candies_taken:int, who_made_turn:str):
    return await bot.send_message(
            userid,
            md.text(
                md.text(who_made_turn),
                md.text(emoji.emojize(":candy:") + ' взято:', md.code(last_candies_taken)),
                md.text(emoji.emojize(":candy:") + ' осталось:', md.bold(CandiesGameState.candies_left)),
                md.text(f'Юный падаван {username} {CandiesGameState.player_one_candies_count} ' + emoji.emojize(":candy:") + ' имеет:'),
                md.text(f'Магистр БОТ {CandiesGameState.player_two_candies_count} ' + emoji.emojize(":candy:") + ' завоевал'),
                sep='\n',
            ), parse_mode=ParseMode.MARKDOWN
        )

@dispatcher.message_handler(commands=['start'])
async def bot_started_handler(message: types.Message):
    await bot.send_message(message.from_user.id, 
                           text = f'Приветствую тебя, мой юный падаван {message.from_user.first_name}')

@dispatcher.message_handler(commands=['help'])
async def help_asked_handler(message: types.Message):
    await bot.send_message(message.from_user.id, 
                           text = f'напиши "/letsplay" или "/lp" что бы начать новую игру в конфетки')

@dispatcher.message_handler(state='*', commands='cancel')
@dispatcher.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await drop_state(state)
    await bot.send_message(message.from_user.id, text='Cancelled.', reply_markup=types.ReplyKeyboardRemove())

@dispatcher.message_handler(commands=['letsplay', 'lp'])
async def candies_game_started_handler(message: types.Message):
    # This method will be called only when user starts new candies game
    # Execution steps
    # 1. Define who makes first turn
    # 2. Make BOT's turn in case if bot makes first turn
    # 3. Show new state to user
    # 4. ask user to input count of candies again
    player_starts_round = random.randint(0, 100) % 2 == 0
    if (player_starts_round) :
        await bot.send_message(message.from_user.id, text = f'Юный падаван {message.from_user.first_name}, ты делаешь первый ход')
    else: 
        # 2. Make BOT's turn in case if bot makes first turn
        await bot.send_message(message.from_user.id, text = f'Магистр БОТ делает первый ход')
        bot_makes_turn_and_update_state()
        # 3. Show new state to user
        await send_update_state_message(message.from_user.id, message.from_user.first_name, CandiesGameState.player_two_last_candies_getted, 'Магистр БОТ делает ход:')
    
    # 4. ask user to input count of candies
    await bot.send_message(message.from_user.id, text=f"Юный падаван {message.from_user.first_name}, твой ход. \nВведи число от 1 до {CandiesGameState.max_candies_count_to_take}")
    await CandiesGameState.player_one_last_candies_getted.set()

@dispatcher.message_handler(lambda message: not message.text.isdigit(), state=CandiesGameState.player_one_last_candies_getted)
async def process_candies_getting_invalid_handler(message: types.Message):
    max_count = CandiesGameState.max_candies_count_to_take if CandiesGameState.candies_left >= CandiesGameState.max_candies_count_to_take else CandiesGameState.candies_left
    return await send_invalid_candies_count_message(message.from_user.id, max_count)

@dispatcher.message_handler(lambda message: message.text.isdigit(), state=CandiesGameState.player_one_last_candies_getted)
async def process_candies_getting_handler(message: types.Message, state: FSMContext):
    # This method will be called only when user inputs count of candies
    # Execution steps
    # 1. Check that count of taken candies is valid
    # 2. Make user's turn and update game state
    # 3. Show new state to user
    # 4. Make BOT's turn and update game state
    # 5. Show new state to user
    # 6. ask user to input count of candies again 
    number = int(message.text)
    # 1. Check that count of taken candies is valid
    max_count = CandiesGameState.max_candies_count_to_take if CandiesGameState.candies_left >= CandiesGameState.max_candies_count_to_take else CandiesGameState.candies_left
    if (number < 1 or number > max_count) :
        return await send_invalid_candies_count_message(message.from_user.id, max_count)
    # 2. Make user's turn and update game state
    await user_makes_turn_and_update_state(number, state)
    # 3. Show new state to user
    if (CandiesGameState.is_game_finished):
        await drop_state(state)
        return await send_win_message(message.from_user.id, f'Юный падаван {message.from_user.first_name}')
    else: await send_update_state_message(message.from_user.id, message.from_user.first_name, number, f'Юный падаван {message.from_user.first_name} делает ход:')
    # 4. Make BOT's turn and update game state
    bot_makes_turn_and_update_state()
    # 5. Show new state to user
    if (CandiesGameState.is_game_finished):
        await drop_state(state)
        return await send_win_message(message.from_user.id, 'Магистр БОТ')
    else: await send_update_state_message(message.from_user.id, message.from_user.first_name, CandiesGameState.player_two_last_candies_getted, 'Магистр БОТ делает ход:')
    # 6. ask user to input count of candies again
    await bot.send_message(message.from_user.id, text=f"Юный падаван {message.from_user.first_name}, твой ход. \nВведи число от 1 до {CandiesGameState.max_candies_count_to_take}")
 
    await CandiesGameState.player_one_last_candies_getted.set()

@dispatcher.message_handler()
async def anything(message: types.Message):
    await message.reply(f'Моя твоя не понимать')