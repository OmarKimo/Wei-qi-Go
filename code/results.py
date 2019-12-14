from arcade.gui import *


class results_Screen:
    def __init__(self, screen_width, screen_height):
        arcade.set_background_color(arcade.color.AERO_BLUE)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.BlackCap = None
        self.BlackScore = None
        self.WhiteCap = None
        self.WhiteScore = None
        self.winner = None

    def setup(self, arr):
        self.winner = arr[0]
        self.BlackCap = arr[1]
        self.BlackScore = arr[2]
        self.WhiteCap = arr[3]
        self.WhiteScore = arr[4]

    def draw(self, supr):
        arcade.start_render()
        supr.on_draw()
        arcade.draw_text(self.winner, 300, 400, arcade.color.BLACK,30)
        arcade.draw_text(self.BlackCap, 300, 300, arcade.color.BLACK,30)
        arcade.draw_text(self.BlackScore, 300, 350, arcade.color.BLACK,30)
        arcade.draw_text(self.WhiteCap, 700, 300, arcade.color.BLACK,30)
        arcade.draw_text(self.WhiteScore, 700, 350, arcade.color.BLACK,30)
        arcade.draw_text("ESC to continue!", 0, 10, arcade.color.BLACK,20)

