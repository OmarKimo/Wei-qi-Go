from __future__ import print_function
# tag::bot_vs_bot[]
from dlgo import agent
from dlgo import goboard_fast as goboard
from dlgo import gotypes
from dlgo.utils import print_board, print_move
import time
import h5py
from dlgo.rl import load_value_agent

def main():
    board_size = 19
    game = goboard.GameState.new_game(board_size)
    fast_policy = agent.load_prediction_agent(h5py.File('test_alphago_sl_policy.h5', 'r'))     #sl
    strong_policy = agent.load_policy_agent(h5py.File('test_alphago_rl_policy.h5', 'r'))       #rl
    value = load_value_agent(h5py.File('test_alphago_value.h5', 'r'))                      #value
    bots = {
        gotypes.Player.black: agent.alphago.AlphaGoMCTS(strong_policy, fast_policy, value),
        gotypes.Player.white: agent.alphago.AlphaGoMCTS(strong_policy, fast_policy, value),
    }
    while not game.is_over():
        time.sleep(0.3)  # <1>

        print(chr(27) + "[2J")  # <2>
        print_board(game.board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.apply_move(bot_move)


if __name__ == '__main__':
    main()

# <1> We set a sleep timer to 0.3 seconds so that bot moves aren't printed too fast to observe
# <2> Before each move we clear the screen. This way the board is always printed to the same position on the command line.
# end::bot_vs_bot[]
