from aiogram.dispatcher.filters.state import State, StatesGroup
import random
from typing import Tuple


class CandiesGameState(StatesGroup):
    candies_left:int = 150
    max_candies_count_to_take:int = 28

    player_one_candies_count:int = 0
    player_two_candies_count:int = 0

    is_game_finished = False

    player_one_last_candies_getted = State()
    player_two_last_candies_getted:int = 0 #player two is bot, not need to create state for it

#functions

def calculate_candies_to_take(max_candies_count_to_take: int, candies_left: int) -> int:
    if (candies_left > 29) :
        return candies_left - 29 if (candies_left > 29 and candies_left <= 57) else random.randint(1, max_candies_count_to_take)
    if (candies_left == 29) :
        #nothing to do here - bot will lose in any case;
        return random.randint(1, max_candies_count_to_take)
    if (candies_left <= 28) :
        #bot wins - need to take all left candies;
        return candies_left

def reduce_candies(player_candies_count: int, 
                   candies_left: int, 
                   max_candies_count_to_take: int,
                   reduce_candies_func) -> Tuple[bool, int, int, int]:
    is_game_finished = False
    player_takes_candies_count = reduce_candies_func(max_candies_count_to_take, candies_left)
    player_candies_count += player_takes_candies_count
    candies_left -= player_takes_candies_count
    if (candies_left <= 0) : is_game_finished = True
    return is_game_finished, player_candies_count, candies_left, player_takes_candies_count