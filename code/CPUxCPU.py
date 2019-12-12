from arcade.gui import *

import os

SOUND_ON =True
OP_LOGO="logo/opacity_logo2.png"
file ="configuration.txt"
ip ="please enter ip in configuration file"
port="please enter port number in configuration file"

def configuration(file):
    try:
        f=open(file,"r")
        count=0
        global ip
        for line in f:
            line = line.split()
            if(count == 0):
                ip= line[0]
                count = count+1
            elif (count == 1):
                port = line[0]
                count= count+1
    except:
        port = "Error in configuration file"
        ip = "Error in configuration file"



class PlayButton(TextButton):
    def __init__(self, game, x=0, y=0, width=100, height=40, text="Play", theme=None):
        super().__init__(x, y, width, height, text, theme=theme)
        self.game = game
        
    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.game.pause = False
            self.pressed = False
            return True
        return False

class cvc_Setting():
    def __init__(self,screen_width,screen_height):
        global file
        configuration(file)
        self.logo=arcade.load_texture(OP_LOGO)
        self.logo_center_x=screen_width/2.0
        self.logo_center_y=screen_height/2.0
        self.logo_width= screen_width/2.0
        self.logo_height= screen_width/2.0

        self.pause = False
        self.text1 = "IP: "
        self.text1_x = 200
        self.text1_y = 400
        self.text1_font_size = 40

        self.text2 = "Port:"
        self.text2_x=200
        self.text2_y=300
        self.text2_font_size = 40


        self.text3 = ip
        self.text3_x=400
        self.text3_y=400
        self.text3_font_size = 40

        self.text4 = ip
        self.text4_x=400
        self.text4_y=300
        self.text4_font_size = 40

        self.speed = 0
        self.theme = None
        self.theme2 =None
        self.theme3 = None
        self.theme4 = None

        self.text_error = "  "

    def set_button_textures(self):
        normal = arcade.color.WHITE
        hover = arcade.color.BLACK
        clicked = arcade.color.BLUE
        locked = arcade.color.ALMOND
        ttry = "images/button_black.png"
        normalwhite= "images/button_white3.png"
        play="images/play2.png"
        back="images/back.png"
        forward="images/forward.png"
        self.theme4.add_button_textures(back,back,back,back)
        self.theme5.add_button_textures(forward,forward,forward,forward)
        #self.theme.add_button_textures(normalwhite,normalwhite,normalwhite,normalwhite)
        #self.theme.add_button_textures(play,play,play,play)
        self.theme.add_button_textures(ttry,ttry,ttry,ttry)
        #self.theme3.add_button_textures(ttry,ttry,ttry,ttry)

        
        #self.theme4.add_button_textures(normalwhite,normalwhite,normalwhite,normalwhite)

    def setup_theme(self):
        self.theme = Theme()
        self.theme.set_font(24, arcade.color.WHITE_SMOKE)
        self.theme4=Theme()
        self.theme4.set_font(40,arcade.color.BLACK)

        self.theme5=Theme()
        self.theme5.set_font(20, arcade.color.WHITE)
        '''
        self.theme2=Theme()
        self.theme2.set_font(20, arcade.color.WHITE)
        
        self.theme3=Theme()
        self.theme2.set_font(20, arcade.color.WHITE)

        self.theme4=Theme()
        self.theme4.set_font(40,arcade.color.BLACK)
        '''
        self.set_button_textures()


    def set_buttons(self, button_list, game):
        button_list.append(PlayButton(game, 640, 100, 150, 150, theme=self.theme))

        #self.button_list.append(Forward(self, 700, 100, 100, 100, theme=self.theme5))
        '''
        self.button_list.append(Button13x13(self, 400, 380, 100, 100, theme=self.theme2))
        
        self.button_list.append(Button19x19(self, 400, 260, 100, 100, theme=self.theme2))

        self.button_list.append(SaveButton(self, 650,100,150,150,theme=self.theme4))
        '''
        return button_list

    def setup(self, button_list, game):
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.CADET_GREY)
        self.setup_theme()
        return self.set_buttons(button_list, game)

    def draw(self, supr):
        arcade.start_render()
        arcade.draw_texture_rectangle(self.logo_center_x,self.logo_center_y, self.logo_width,self.logo_height, self.logo)
        
        supr.on_draw()
        arcade.draw_text(self.text1, self.text1_x, self.text1_y, arcade.color.BLACK, self.text1_font_size)
        arcade.draw_text(self.text2, self.text2_x, self.text2_y, arcade.color.BLACK, self.text2_font_size)
        arcade.draw_text(self.text3, self.text3_x, self.text3_y, arcade.color.BLACK, self.text3_font_size)
        arcade.draw_text(self.text4, self.text4_x, self.text4_y, arcade.color.BLACK, self.text4_font_size)
        arcade.draw_text(self.text_error, 320,600, arcade.color.BLACK, self.text1_font_size)

    def mouse_release(self, button_list):
        for button in button_list:
            t = button.on_release()
            if t:
                return [ip,port]
        return -1

    def connection_error(self):
        self.text_error = "Cannot connect to server now!\nplease,check configuration file!"
'''
    def update(self, delta_time):
        if self.pause:
            return

        if self.text_x < 0 or self.text_x > self.width:
            self.speed = -self.speed
        self.text_x += self.speed
'''       
