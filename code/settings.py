from arcade.gui import *

import os

SOUND_ON = True
OP_LOGO = "logo/opacity_logo2.png"


class Button9x9(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="9 x 9", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = False
            self.pressed = False
            return "9"
        return "False"

class ButtonPlayer1(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Player 1", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = False
            self.pressed = False
            return "You are Player 1"
        return "False"

class ButtonPlayer2(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Player 2", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = False
            self.pressed = False
            return "You are Player 2"
        return "False"

class Button13x13(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="13 x 13", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.pressed = False
            return "13"
        return "False"


class Button19x19(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="19 x 19", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            # if SOUND_ON:
            #     SOUND_ON=False
            # else:
            #     SOUND_ON=True
            self.pressed = False
            return "19"
        return "False"


class SaveButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Save", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.pressed = False
            # TO DO: save everything before closing
            # close current settings
            arcade.close_window()


class pvc_Setting():
    def __init__(self,screen_width,screen_height):


        self.logo = arcade.load_texture(OP_LOGO)
        self.logo_center_x = screen_width/2.0
        self.logo_center_y = screen_height/2.0
        self.logo_width = screen_width/2.0
        self.logo_height = screen_width/2.0

        self.pause = False
        self.text = "Choose Board size: "
        self.text_x = 20
        self.text_y = 500
        self.text_font_size = 30

        self.text1 = "Choose Player:"
        self.text1_x = 600
        self.text1_y = 500
        self.text1_font_size = 30

        self.speed = 0
        self.theme = None
        self.theme2 = None
        self.theme3 = None
        self.theme4 = None

        self.player_txt = "Choose your turn!"

    def set_button_textures(self):
        normal = arcade.color.WHITE
        hover = arcade.color.BLACK
        clicked = arcade.color.BLUE
        locked = arcade.color.ALMOND
        ttry = "images/button_black.png"
        back = "images/back.png"
        forward = "images/forward.png"
        self.theme.add_button_textures(ttry, ttry, ttry, ttry)
        self.theme2.add_button_textures(ttry, ttry, ttry, ttry)
        self.theme3.add_button_textures(ttry, ttry, ttry, ttry)
        self.theme4.add_button_textures(back, back, back, back)
        self.theme5.add_button_textures(forward, forward, forward, forward)
        self.theme6.add_button_textures(ttry, ttry, ttry, ttry)
        self.theme7.add_button_textures(ttry, ttry, ttry, ttry)

        normalwhite = "images/button_white3.png"
        # self.theme4.add_button_textures(normalwhite,normalwhite,normalwhite,normalwhite)

    def setup_theme(self):
        self.theme = Theme()
        self.theme.set_font(24, arcade.color.WHITE)

        self.theme2 = Theme()
        self.theme2.set_font(20, arcade.color.WHITE)

        self.theme3 = Theme()
        self.theme2.set_font(20, arcade.color.WHITE)

        self.theme4 = Theme()
        self.theme4.set_font(40, arcade.color.BLACK)

        self.theme5 = Theme()
        self.theme5.set_font(20, arcade.color.WHITE)

        self.theme6 = Theme()
        self.theme6.set_font(20, arcade.color.WHITE)

        self.theme7 = Theme()
        self.theme7.set_font(20, arcade.color.WHITE)

        self.set_button_textures()

    def set_buttons(self, button_list, game):
        button_list.append(Button9x9(game, 400, 500, 100, 100, theme=self.theme))

        button_list.append(Button13x13(game, 400, 380, 100, 100, theme=self.theme2))

        button_list.append(Button19x19(game, 400, 260, 100, 100, theme=self.theme2))
        button_list.append(ButtonPlayer1(game, 950, 500, 150, 150, theme=self.theme6))
        button_list.append(ButtonPlayer2(game, 950, 260, 150, 150, theme=self.theme7))

        # self.button_list.append(SaveButton(self, 650,100,150,150,theme=self.theme4))
        return button_list

    def setup(self, button_list, game):
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        arcade.set_background_color(arcade.color.CADET_GREY)
        self.setup_theme()
        return self.set_buttons(button_list, game)

    def draw(self, supr):
        arcade.draw_texture_rectangle(self.logo_center_x, self.logo_center_y, self.logo_width, self.logo_height,
                                      self.logo)

        supr.on_draw()
        arcade.draw_text(self.text, self.text_x, self.text_y, arcade.color.BLACK, self.text_font_size)
        arcade.draw_text(self.text1, self.text1_x, self.text1_y, arcade.color.BLACK, self.text1_font_size)
        arcade.draw_text(self.player_txt, 340, 640, arcade.color.BLACK, self.text1_font_size)

    def mouse_release(self, button_list):
        for button in button_list:
            t = button.on_release()
            if t != "False" and not t.__contains__("You are Player"):
                return int(t)
            elif t.__contains__("You are Player"):
                self.player_txt = t
                return int(t[-1])
        return -1


'''
    def update(self):
        if self.pause:
            return

        if self.text_x < 0 or self.text_x > self.width:
            self.speed = -self.speed
        self.text_x += self.speed
'''
