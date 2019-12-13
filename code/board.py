import arcade
import h5py
import numpy
import time
import copy
from dlgo.gotypes import Player, Point
from dlgo.scoring import compute_game_result
from dlgo import zobrist
import dlgo.utils
from dlgo.goboard_slow import Move
from dlgo.agent.helpers import is_point_an_eye

#bot define
from dlgo import goboard_fast as goboard
from dlgo import agent, gotypes
from dlgo.rl import load_value_agent

bot_board_size = 19
game = goboard.GameState.new_game(bot_board_size)
fast_policy = agent.load_prediction_agent(h5py.File('test_alphago_sl_policy.h5', 'r'))     #sl
strong_policy = agent.load_policy_agent(h5py.File('test_alphago_rl_policy.h5', 'r'))       #rl
value = load_value_agent(h5py.File('test_alphago_value.h5', 'r'))                      #value
bots = {
    gotypes.Player.black: agent.alphago.AlphaGoMCTS(strong_policy, fast_policy, value),
    gotypes.Player.white: agent.alphago.AlphaGoMCTS(strong_policy, fast_policy, value),
    #gotypes.Player.white: agent.naive.RandomBot()
}
Random_Bot=agent.naive.RandomBot()
player_turn={
    1 : gotypes.Player.white,
    2 : gotypes.Player.black,
}







# Set up the constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
INFO_SCREEN_HEIGHT = 50
INFO_SCREEN_WIDTH = SCREEN_WIDTH
FORCE_ASPECT_RATIO = 1
PLAYABLE_SCREEN_HEIGHT = SCREEN_HEIGHT - INFO_SCREEN_HEIGHT
PLAYABLE_SCREEN_WIDTH = INFO_SCREEN_WIDTH
FULL_SCREEN = False
SCREEN_TITLE = "Go Wéiqí"

BOARD_SIZE = None
STONE_RAD = None
GRID_LINE_WIDTH = 2
INFO_LINE_WIDTH = 2 * GRID_LINE_WIDTH


def get_x_corresponding_to_col(col):
    return SCREEN_WIDTH / (BOARD_SIZE[0] + 1) + col * SCREEN_WIDTH / (BOARD_SIZE[0] + 1)


def get_y_corresponding_to_row(row):
    return PLAYABLE_SCREEN_HEIGHT - (
            PLAYABLE_SCREEN_HEIGHT / (BOARD_SIZE[1] + 1) + row * PLAYABLE_SCREEN_HEIGHT / (BOARD_SIZE[1] + 1))


DISTANCE_BETWEEN_GRID_LINES = None

WHITE = arcade.color.WHITE
BLACK = arcade.color.BLACK
GREEN = arcade.color.GREEN
GRID_LINE_COLOR = BLACK
INFO_LINE_COLOR = BLACK
PLAYER_1_FILL_COLOR = WHITE
PLAYER_1_OUTLINE_COLOR = WHITE
PLAYER_2_FILL_COLOR = BLACK
PLAYER_2_OUTLINE_COLOR = BLACK
TEXT_COLOR = BLACK
BACKGROUND_COLOR = WHITE
FONT_SIZE = 15

BOARD_IMAGE = "board.jfif"


class Stone:

    def __init__(self, center_x, center_y, rad, fill_color, outline_color):
        self.center_x = center_x
        self.center_y = center_y
        self.rad = rad
        self.fill_color = fill_color
        self.outline_color = outline_color

    def is_center(self, x, y):
        if self.center_x == x and self.center_y == y:
            return True
        return False

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.rad, self.fill_color)
        arcade.draw_circle_outline(self.center_x, self.center_y, self.rad, self.outline_color)


class Game_Logic:
    def __init__(self,board_size):
        global BOARD_SIZE
        global STONE_RAD
        global DISTANCE_BETWEEN_GRID_LINES
        global bots,game,bot_board_size
        self.stone_list = None  # contains all of the stones objects and this is the list to draw
        self.stone_matrix = None  # contains the position (i,j) and the color of each stone at the current stage
        self.board_img = None  # contains the texture of the board
        self.p_v_c_stone = None  # contains the data of the stone moving with the mouse

        self.MODE = None  # 0 for CPU VS CPU , 1 for Player VS CPU
        self.CURRENT_TURN = None  # 1 for player 1 ,2 for player 2
        self.WHO_IS_CPU = None  # 1 if player 1 is the cpu, 2 if player 2 is the cpu. checked only in the Player VS CPU
        # mode

        self.PLAYER_1_REMAINING_TIME = None
        self.PLAYER_1_SCORE = None
        self.PLAYER_1_N_OF_PRISONERS = None

        self.PLAYER_2_REMAINING_TIME = None
        self.PLAYER_2_SCORE = None
        self.PLAYER_2_N_OF_PRISONERS = None

        self.cpu_hint_x_y = None  # the position of the hint
        self.hint_rad = None  # changes over time
        self.hint_text = None
        self.increase_hint_rad = None
        self.first_stone = None  # first play
        self.second_stone = None
        self.sound = None
        self.music = None
        BOARD_SIZE = board_size
        bot_board_size = board_size
        if bot_board_size < 18:
            game = goboard.GameState.new_game(bot_board_size)
            bots = {
                gotypes.Player.white: agent.naive.RandomBot(),
                gotypes.Player.black: agent.naive.RandomBot(),
            }

        STONE_RAD = min(SCREEN_WIDTH / (BOARD_SIZE[0] + 1), PLAYABLE_SCREEN_HEIGHT / (BOARD_SIZE[1] + 1)) / 2.5
        DISTANCE_BETWEEN_GRID_LINES = min((get_x_corresponding_to_col(1) - get_x_corresponding_to_col(0)),
                                          (get_y_corresponding_to_row(0) - get_y_corresponding_to_row(1)))

    def setup(self, MODE, WHO_IS_CPU):
        """ Set up the game and initialize the variables. """
        arcade.set_background_color(BACKGROUND_COLOR)
        self.stone_list = []
        self.stone_matrix = [[0 for i in range(BOARD_SIZE[0])] for j in range(BOARD_SIZE[1])]
        self.board_img = arcade.load_texture(BOARD_IMAGE)
        self.p_v_c_stone = None

        self.MODE = MODE  # 0 for CPU VS CPU , 1 for Player VS CPU
        self.CURRENT_TURN = 1  # 1 for player 1 ,2 for player 2
        self.WHO_IS_CPU = WHO_IS_CPU  # 1 if player 1 is the cpu, 2 if player 2 is the cpu. checked only in the
        # Player VS CPU mode

        self.PLAYER_1_REMAINING_TIME = 30
        self.PLAYER_1_SCORE = 0
        self.PLAYER_1_N_OF_PRISONERS = 0

        self.PLAYER_2_REMAINING_TIME = 30
        self.PLAYER_2_SCORE = 0
        self.PLAYER_2_N_OF_PRISONERS = 0

        self.cpu_hint_x_y = [4 * -STONE_RAD, 4 * -STONE_RAD]  # the position of the hint
        self.hint_rad = 0  # changes over time
        self.hint_text = ""
        self.increase_hint_rad = True
        self.first_stone = True  # first play
        self.second_stone = True
        self.sound = arcade.load_sound("sound.mp3")
        #game.next_player = player_turn[self.CURRENT_TURN]

    def change_turn(self):
        if self.CURRENT_TURN == 1:
            self.CURRENT_TURN = 2
        else:
            self.CURRENT_TURN = 1

    def player_vs_cpu_moving_stone(self, mouse_x, mouse_y):
        # draw a stone that walks with the mouse in player turn only
        self.p_v_c_stone = None
        if self.MODE == 0 or self.CURRENT_TURN == self.WHO_IS_CPU:
            return
        if self.CURRENT_TURN == 1:
            fill_col = PLAYER_1_FILL_COLOR
            outline_col = PLAYER_1_OUTLINE_COLOR
        else:
            fill_col = PLAYER_2_FILL_COLOR
            outline_col = PLAYER_2_OUTLINE_COLOR
        self.p_v_c_stone = Stone(mouse_x, mouse_y, STONE_RAD / 2.0, fill_col, outline_col)

    def place_player_stone(self, mouse_x, mouse_y):
        global game, bots,Random_Bot,player_turn
        if self.MODE == 0 or self.CURRENT_TURN == self.WHO_IS_CPU:
            return

        i = 0
        found = False
        while i < BOARD_SIZE[0]:
            if found:
                break
            if abs(mouse_x - self.get_x_corresponding_to_col(i)) < DISTANCE_BETWEEN_GRID_LINES / 2.5:
                j = 0
                while j < BOARD_SIZE[1]:
                    if abs(mouse_y - self.get_y_corresponding_to_row(j)) < DISTANCE_BETWEEN_GRID_LINES / 2.5:
                        found = True
                        break
                    else:
                        j = j + 1
                i = i + 1
            else:
                i = i + 1

        if not found:
            return False
        i = i - 1

        if self.stone_matrix[j][i] == 0:
            #self.stone_matrix[j][i] = self.CURRENT_TURN
            row = game.board.num_rows-j
            col = i + 1
            #game.next_player=player_turn[self.CURRENT_TURN]
            Player_move = Random_Bot.make_move(game,row=row,col=col)
            if not Player_move:
                return False
            game = game.apply_move(Player_move)
            return True

        return False

    def update_stone_matrix(self, mouse_x, mouse_y):
        global game,bots,player_turn
        """ update stone matrix from the other team"""
        stone_placed = False

        if self.MODE == 1 and self.CURRENT_TURN == self.WHO_IS_CPU and not self.first_stone:
            # get hint from cpu
            bot_move = bots[player_turn[self.CURRENT_TURN]].select_move(game)
            if not bot_move:
                bot_move = goboard.Move(is_resign=True)
                return
            rx = bot_move.point.col-1
            ry = game.board.num_rows-bot_move.point.row
            self.cpu_hint_x_y = [self.get_x_corresponding_to_col(rx), self.get_y_corresponding_to_row(ry)]
            self.hint_text = "    The best \n" \
                             "\n   position to \n" \
                             "\n     play was\n" \
                             "\n       (" + str(rx + 1) + \
                             "," + str(BOARD_SIZE[1] - ry) + ")"
        else:
            # remove hint
            self.cpu_hint_x_y = [4 * -STONE_RAD, 4 * -STONE_RAD]

        if self.MODE == 0 or self.CURRENT_TURN == self.WHO_IS_CPU:
            bot_move = bots[player_turn[self.CURRENT_TURN]].select_move(game)
            if not bot_move:
                bot_move = goboard.Move(is_resign=True)
                return
            game = game.apply_move(bot_move)

            for row in range(1, game.board.num_rows+1):
                for col in range(0, game.board.num_cols+1):
                    stone =  game.board.get(gotypes.Point(row=row, col=col))
                    if stone == gotypes.Player.white:
                        self.stone_matrix[game.board.num_rows-row][col-1] = 1
                    elif stone == gotypes.Player.black:
                        self.stone_matrix[game.board.num_rows-row][col-1] = 2
                    else:
                        self.stone_matrix[game.board.num_rows-row][col-1] = 0
            #dlgo.utils.print_board(game.board)
            stone_placed = True
        else:  # if this is player turn
            stone_placed= self.place_player_stone(mouse_x, mouse_y)


        if stone_placed:
            arcade.play_sound(self.sound)
            if not self.first_stone:
                self.second_stone = False
            self.first_stone = False
            self.change_turn()

    def get_x_corresponding_to_col(self, col):
        if FORCE_ASPECT_RATIO == 0:
            return get_x_corresponding_to_col(col)
        else:
            return (SCREEN_WIDTH - BOARD_SIZE[0] * DISTANCE_BETWEEN_GRID_LINES) / 2.0 + (
                    col * DISTANCE_BETWEEN_GRID_LINES)

    def get_y_corresponding_to_row(self, row):
        return PLAYABLE_SCREEN_HEIGHT - (
                PLAYABLE_SCREEN_HEIGHT / (BOARD_SIZE[1] + 1) + row * PLAYABLE_SCREEN_HEIGHT / (BOARD_SIZE[1] + 1))

    def game_update(self, mouse_x=-1, mouse_y=-1):
        self.update_stone_matrix(mouse_x, mouse_y)
        self.stone_list.clear()
        row = 0
        updated_row_positions = []  # to store all the row values of the changed stones
        updated_col_positions = []  # to store the corresponding col values of the changed stones
        updated_count = 0  # counts the number of updated positions
        while row < BOARD_SIZE[0]:
            col = 0
            while col < BOARD_SIZE[1]:
                if self.stone_matrix[row][col] != 0:
                    updated_row_positions.append(row)
                    updated_col_positions.append(col)
                    updated_count = updated_count + 1
                col = col + 1
            row = row + 1

        i = 0  # to loop on the updated positions
        while i < updated_count:
            # to determine positions on screen
            x = self.get_x_corresponding_to_col(updated_col_positions[i])
            y = self.get_y_corresponding_to_row(updated_row_positions[i])

            if self.stone_matrix[updated_row_positions[i]][updated_col_positions[i]] == 1:
                # if position is player (1)
                s = Stone(x, y, STONE_RAD, PLAYER_1_FILL_COLOR, PLAYER_1_OUTLINE_COLOR)
                self.stone_list.append(s)

            elif self.stone_matrix[updated_row_positions[i]][updated_col_positions[i]] == 2:
                # if position is player (2)
                s = Stone(x, y, STONE_RAD, PLAYER_2_FILL_COLOR, PLAYER_2_OUTLINE_COLOR)
                self.stone_list.append(s)
            i = i + 1

    def draw_board_image(self):
        playable_center_x = PLAYABLE_SCREEN_WIDTH / 2.0
        playable_center_y = PLAYABLE_SCREEN_HEIGHT / 2.0
        arcade.draw_texture_rectangle(playable_center_x, playable_center_y, PLAYABLE_SCREEN_WIDTH,
                                      PLAYABLE_SCREEN_HEIGHT, self.board_img)

    def draw_info_line(self):
        y = PLAYABLE_SCREEN_HEIGHT
        x_start = 0
        x_end = SCREEN_WIDTH
        arcade.draw_line(x_start, y, x_end, y, INFO_LINE_COLOR, INFO_LINE_WIDTH)

    def draw_grid(self):
        # draw vertical lines

        y_start = self.get_y_corresponding_to_row(BOARD_SIZE[0] - 1)
        y_end = self.get_y_corresponding_to_row(0)

        for i in range(BOARD_SIZE[0]):
            x_start = x_end = self.get_x_corresponding_to_col(i)
            arcade.draw_line(x_start, y_start, x_end, y_end, GRID_LINE_COLOR, GRID_LINE_WIDTH)
            arcade.draw_text(str(i + 1), x_start - .5 * FONT_SIZE, y_end + .9 * STONE_RAD, GRID_LINE_COLOR, FONT_SIZE)
            arcade.draw_text(str(i + 1), x_start - .5 * FONT_SIZE, y_start - 2.1 * STONE_RAD, GRID_LINE_COLOR,
                             FONT_SIZE)

        # draw horizontal lines

        x_start = self.get_x_corresponding_to_col(BOARD_SIZE[1] - 1)
        x_end = self.get_x_corresponding_to_col(0)
        for i in range(BOARD_SIZE[1]):
            y_start = y_end = self.get_y_corresponding_to_row(i)
            arcade.draw_line(x_start, y_start, x_end, y_end, GRID_LINE_COLOR, GRID_LINE_WIDTH)
            arcade.draw_text(str(BOARD_SIZE[1] - i), x_start + 1.5 * STONE_RAD, y_start - .5 * FONT_SIZE,
                             GRID_LINE_COLOR, FONT_SIZE)
            arcade.draw_text(str(BOARD_SIZE[1] - i), x_end - 2.4 * STONE_RAD, y_start - .5 * FONT_SIZE, GRID_LINE_COLOR,
                             FONT_SIZE)

    def draw_info(self):
        start_x = 0
        start_y = SCREEN_HEIGHT - FONT_SIZE
        arcade.draw_text("PLAYER 1 REMAINING TIME : " + str(self.PLAYER_1_REMAINING_TIME), start_x, start_y, TEXT_COLOR
                         , FONT_SIZE)

        start_y = start_y - FONT_SIZE
        arcade.draw_text("PLAYER 1 SCORE : " + str(self.PLAYER_1_SCORE), start_x, start_y, TEXT_COLOR
                         , FONT_SIZE)

        start_y = start_y - FONT_SIZE
        arcade.draw_text("PLAYER 1 NUMBER OF PRISONERS : " + str(self.PLAYER_1_N_OF_PRISONERS), start_x, start_y,
                         TEXT_COLOR
                         , FONT_SIZE)

        start_x = INFO_SCREEN_WIDTH * 2.82 / 4
        start_y = SCREEN_HEIGHT - FONT_SIZE

        arcade.draw_text("PLAYER 2 REMAINING TIME : " + str(self.PLAYER_1_REMAINING_TIME), start_x, start_y, TEXT_COLOR
                         , FONT_SIZE)

        start_y = start_y - FONT_SIZE
        arcade.draw_text("PLAYER 2 SCORE : " + str(self.PLAYER_1_SCORE), start_x, start_y, TEXT_COLOR
                         , FONT_SIZE)

        start_y = start_y - FONT_SIZE
        arcade.draw_text("PLAYER 2 NUMBER OF PRISONERS : " + str(self.PLAYER_1_N_OF_PRISONERS), start_x, start_y,
                         TEXT_COLOR
                         , FONT_SIZE)

        start_x = INFO_SCREEN_WIDTH * .38
        start_y = SCREEN_HEIGHT - FONT_SIZE * 2
        arcade.draw_text("CURRENT TURN IS PLAYER : " + str(self.CURRENT_TURN), start_x, start_y, TEXT_COLOR
                         , FONT_SIZE)

    def draw_stones(self):
        for st in self.stone_list:
            st.draw()
        self.p_v_c_stone.draw()

    def draw_hint(self):
        hint_step = .5
        if self.increase_hint_rad and self.hint_rad < STONE_RAD:
            self.hint_rad = self.hint_rad + hint_step
        elif self.increase_hint_rad and self.hint_rad >= STONE_RAD:
            self.increase_hint_rad = False
            self.hint_rad = self.hint_rad - hint_step
        elif not self.increase_hint_rad and self.hint_rad > 0:
            self.hint_rad = self.hint_rad - hint_step
        else:
            self.increase_hint_rad = True
            self.hint_rad = self.hint_rad + hint_step

        s = Stone(self.cpu_hint_x_y[0], self.cpu_hint_x_y[1], self.hint_rad, GREEN, WHITE)

        s.draw()

        # for the hint text
        if not self.first_stone and not (self.WHO_IS_CPU == 1 and self.second_stone):
            start_x = 0
            start_y = PLAYABLE_SCREEN_HEIGHT / 3
            arcade.draw_text(self.hint_text, start_x, start_y, GREEN, 2 * FONT_SIZE)

    def draw_game(self):
        self.draw_board_image()
        self.draw_info()
        self.draw_info_line()
        self.draw_grid()
        self.draw_stones()
        self.draw_hint()


