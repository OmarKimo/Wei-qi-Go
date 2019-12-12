from board import *
from Introduction import *
from settings import *
from CPUxCPU import *
Main_Menu_View = 0
Board_View = 1
PVC_Setting_View = 2
CVC_Setting_View = 3

def check_connection(IP,Port):
    return True

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FULL_SCREEN)
        self.Intro = None
        self.G = None
        self.PVC_S = None
        self.CVC_S = None
        self.CURRENT_VIEW = Main_Menu_View  # 0 for main menu , 1 for the game , 2 for settings , 3 for pause
        self.MODE = None
        self.WHO_IS_CPU = None
        self.Board_Size = None

    def setup_intro(self):
        self.button_list.clear()
        self.Intro = intro(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.button_list = self.Intro.setup(self.button_list, self)

    def setup_board(self):
        self.button_list.clear()
        self.G = Game_Logic(self.Board_Size)
        self.G.setup(self.MODE, self.WHO_IS_CPU)

    def setup_PVC_S(self):
        self.button_list.clear()
        self.PVC_S = pvc_Setting(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.button_list = self.PVC_S.setup(self.button_list, self)

    def setup_CVC_S(self):
        self.button_list.clear()
        self.CVC_S = cvc_Setting(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.button_list = self.CVC_S.setup(self.button_list, self)

    def setup(self):
        self.setup_intro()

    def on_key_release(self, key, modifiers):
        """ Called whenever a user releases a key. """
        if self.CURRENT_VIEW == Main_Menu_View:  # the menu
            if key == arcade.key.ESCAPE:
                self.close()
        elif self.CURRENT_VIEW == Board_View:  # the game
            if key == arcade.key.ESCAPE:
                self.setup_intro()
                self.CURRENT_VIEW = Main_Menu_View
                self.WHO_IS_CPU = None
        elif self.CURRENT_VIEW == PVC_Setting_View:  # the settings
            if key == arcade.key.ESCAPE:
                self.setup_intro()
                self.CURRENT_VIEW = Main_Menu_View
                self.WHO_IS_CPU = None
        elif self.CURRENT_VIEW == CVC_Setting_View:  # the pause
            if key == arcade.key.ESCAPE:
                self.setup_intro()
                self.CURRENT_VIEW = Main_Menu_View

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called to update our objects. Happens approximately 60 times per second."""
        if self.CURRENT_VIEW == Main_Menu_View:  # the menu
            None
        elif self.CURRENT_VIEW == Board_View:  # the game
            self.G.player_vs_cpu_moving_stone(x, y)
        elif self.CURRENT_VIEW == PVC_Setting_View:  # the settings
            None
        elif self.CURRENT_VIEW == CVC_Setting_View:  # the pause
            None

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Called when a user releases a mouse button.
        """
        if self.CURRENT_VIEW == Main_Menu_View:  # the menu
            temp = self.Intro.mouse_release(self.button_list)
            if temp == 0:
                self.MODE = temp
                self.CURRENT_VIEW = CVC_Setting_View
                self.Board_Size = (19, 19)
                self.setup_CVC_S()
            elif temp == 1:
                self.MODE = temp
                self.CURRENT_VIEW = PVC_Setting_View
                self.setup_PVC_S()
        elif self.CURRENT_VIEW == Board_View:  # the game
            self.G.game_update(x, y)
        elif self.CURRENT_VIEW == PVC_Setting_View:  # the settings
            temp = self.PVC_S.mouse_release(self.button_list)
            if temp == 1:
                self.WHO_IS_CPU = 2
            elif temp == 2:
                self.WHO_IS_CPU = 1

            if temp == 9 and self.WHO_IS_CPU is not None:
                self.Board_Size = (9, 9)
                self.CURRENT_VIEW = Board_View
                self.setup_board()
            elif temp == 13 and self.WHO_IS_CPU is not None:
                self.Board_Size = (13, 13)
                self.CURRENT_VIEW = Board_View
                self.setup_board()
            elif temp == 19 and self.WHO_IS_CPU is not None:
                self.Board_Size = (19, 19)
                self.CURRENT_VIEW = Board_View
                self.setup_board()
        elif self.CURRENT_VIEW == CVC_Setting_View:  # the pause
            temp = self.CVC_S.mouse_release(self.button_list)
            if temp != -1:
                if check_connection(temp[0],temp[1]):
                    self.Board_Size = (19, 19)
                    self.CURRENT_VIEW = Board_View
                    self.setup_board()
                else:
                    self.CVC_S.connection_error()


    def on_update(self, dt):
        """ update everything """
        if self.CURRENT_VIEW == Main_Menu_View:  # the menu
            self.Intro.update(self.width)
        elif self.CURRENT_VIEW == Board_View:  # the game
            self.G.game_update()
        elif self.CURRENT_VIEW == PVC_Setting_View:  # the settings
            None
        elif self.CURRENT_VIEW == CVC_Setting_View:  # the pause
            None
    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()
        if self.CURRENT_VIEW == Main_Menu_View:  # the menu
            self.Intro.draw(super())
        elif self.CURRENT_VIEW == Board_View:  # the game
            self.G.draw_game()
        elif self.CURRENT_VIEW == PVC_Setting_View:  # the settings
            self.PVC_S.draw(super())
        elif self.CURRENT_VIEW == CVC_Setting_View:  # the pause
            self.CVC_S.draw(super())



def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
