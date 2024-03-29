from .screen import Screen
from pygame.image import load
from pygame.font import Font
from utils import Network


class MainMenu(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.network = Network()
        self.font = Font(None, 30)
        self.sound_on = True
        self.music_on = True

        # load the assets
        self.logo = load("assets/logo.png").convert_alpha()
        self.main_menu = load("assets/mainmenu.png").convert_alpha()
        self.register_login = load("assets/register_login.png").convert_alpha()
        self.buttons = load("assets/buttons.png").convert_alpha()

    def draw(self):
        Screen.draw(self)

        # draw the main menu
        self.pg_screen.blit(self.logo, (5, 60))
        self.pg_screen.blit(self.register_login, (150, 5))
        self.pg_screen.blit(self.main_menu, (60, 250))
        s = 64 - self.sound_on * 64
        self.pg_screen.blit(self.buttons, (0, 415), (s, 0, 64, 64))
        m = 64 - self.music_on * 64
        self.pg_screen.blit(self.buttons, (64, 415), (m, 192, 64, 64))

        # if user is logged in, display their name
        username = self.network._cache["username"]
        if username:
            self._draw_left_align_text(username, (10, 20))

    def _draw_left_align_text(self, text, top_left, color=(0, 0, 0)):
        text = self.font.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.topleft = top_left
        self.pg_screen.blit(text, text_rect)

    def mouse_down(self, pos):
        if self.pos_between(pos, (69, 258), (240, 287)):
            return {"screen": "game_screen", "play_sound": "click"}
        elif self.pos_between(pos, (71, 301), (243, 330)):
            return {"screen": "highscores_screen", "play_sound": "click"}
        elif self.pos_between(pos, (72, 345), (242, 379)):
            return {"screen": "help_screen", "play_sound": "click"}
        elif self.pos_between(pos, (153, 58), (303, 93)):
            return {"screen": "login_screen", "play_sound": "click"}
        elif self.pos_between(pos, (154, 7), (308, 47)):
            return {"screen": "register_screen", "play_sound": "click"}
        elif self.pos_between(pos, (0, 415), (64, 479)):
            self.sound_on = not self.sound_on
            return {"sound": self.sound_on, "play_sound": "click"}
        elif self.pos_between(pos, (64, 415), (128, 479)):
            self.music_on = not self.music_on
            return {"music": self.music_on, "play_sound": "click"}
