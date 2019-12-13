from arcade.gui import *

import os

SOUND_ON =True
OP_LOGO="logo/opacity_logo2.png"
LOGO ="logo/png1.png"


class CPU_X_CPU_Button(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="AI Vs. AI", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game
        
    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.pressed = False
            return 0
        return "False"


class Player_X_CPU_Button(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Player Vs. AI", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True

        

    def on_release(self):
        if self.pressed:
            self.pressed = False
            return 1
        return "False"

class ExitButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game

    def on_press(self):
        self.pressed = True
        

    def on_release(self):
        if self.pressed:
            arcade.close_window()
            self.pressed = False
            return "False"

class intro():
    def __init__(self,screen_width,screen_height):
        self.logo=arcade.load_texture(LOGO)
        self.logo_center_x=screen_width/2.0
        self.logo_center_y=screen_height/2.0
        self.logo_width= screen_width/2.0
        self.logo_height= screen_width/2.0
        self.pause = False
        self.text = "Graphical User Interface"
        self.text_x = 0
        self.text_y = 300
        self.text_font_size = 40
        self.speed = 1
        self.theme = None
        self.theme2= None
        self.extra_text = None



    def set_button_textures(self):
        ttry = "images/button_black.png"
        self.theme.add_button_textures(ttry,ttry,ttry,ttry)

        exit ="images/exit4.png"
        self.theme2.add_button_textures(exit,exit,exit,exit)

    def setup_theme(self):
        self.theme = Theme()
        self.theme.set_font(24, arcade.color.WHITE)

        self.theme2= Theme()
        self.set_button_textures()
 
    def set_buttons(self,button_list,game):
        button_list.append(CPU_X_CPU_Button(game, 200, 550, 300, 300, theme=self.theme))
        button_list.append(Player_X_CPU_Button(game, 200, 200, 300, 300, theme=self.theme))
        button_list.append(ExitButton(game,1150,140,200,200,theme=self.theme2))
        return button_list

    def setup(self,button_list,game,text):
        arcade.set_background_color(arcade.color.CADET_BLUE)
        self.setup_theme()
        sound = arcade.load_sound("s.mp3")
        arcade.play_sound(sound)
        self.extra_text = text
        return self.set_buttons(button_list,game)


    def draw(self,supr):
        arcade.draw_texture_rectangle(self.logo_center_x,self.logo_center_y, self.logo_width,self.logo_height, self.logo)
        arcade.draw_text(self.extra_text, 0, 0, arcade.color.BLACK, 40)
        #arcade.draw_text(self.text, self.text_x, self.text_y, arcade.color.BLACK, self.text_font_size)
        supr.on_draw()

    def update(self,width):
        if self.pause:
            return
        if self.text_x < 0 or self.text_x > width:
            self.speed = -self.speed
        self.text_x += self.speed

    def mouse_release(self,button_list):
        for button in button_list:
            t = button.on_release()
            if t != "False":
                return t
        return -1




        


