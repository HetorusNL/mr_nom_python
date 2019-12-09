from .screen import Screen
from utils import Network
from pygame.image import load
from pygame.font import Font


class HighscoresScreen(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.network = Network()
        self.font = Font(None, 30)

        self.fetch_global_highscores = True
        self.fetch_local_highscores = True
        self.highscore_page_idx = 0

        # load the assets
        self.mainmenu = load("assets/mainmenu.png")
        self.buttons = load("assets/buttons.png").convert_alpha()

    def update(self, delta_time):
        if self.highscore_page_idx == 0 and self.fetch_global_highscores:
            self.fetch_global_highscores = False
            result = self.network.fetch_global_highscores()
            if not result["result"]:
                print(result["status"])
            print(result)

        if self.highscore_page_idx == 1 and self.fetch_local_highscores:
            self.fetch_local_highscores = False
            result = self.network.fetch_local_highscores()
            if not result["result"]:
                print(result["status"])
            print(result)

    def draw(self):
        Screen.draw(self)

        # draw the current highscore screen text
        string = "GLOBAL" if self.highscore_page_idx == 0 else "PERSONAL"
        text = self.font.render(string, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (160, 15)
        self.pg_screen.blit(text, text_rect)
        self.pg_screen.blit(self.mainmenu, (64, 20), (0, 42, 196, 42))

        if self.highscore_page_idx == 0:
            if self.network.get_global_highscores().status_code == 200:
                pass
            elif self.network.get_global_highscores().status_code != 0:
                self._draw_failed_highscore_fetch("global")
        elif self.highscore_page_idx == 1:
            if self.network.get_local_highscores().status_code == 200:
                pass
            elif self.network.get_local_highscores().status_code != 0:
                self._draw_failed_highscore_fetch("personal", "not logged in!")

        self.pg_screen.blit(self.buttons, (0, 415), (64, 64, 64, 64))

    def _draw_failed_highscore_fetch(self, which, second=None):
        string1 = "failed to get"
        string2 = "{} highscores!".format(which)
        text = self.font.render(string1, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (160, 85)
        self.pg_screen.blit(text, text_rect)
        text = self.font.render(string2, True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (160, 110)
        self.pg_screen.blit(text, text_rect)

        if second:
            text = self.font.render(second, True, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.center = (160, 240)
            self.pg_screen.blit(text, text_rect)

    def mouse_down(self, pos):
        # first handle specific position
        if self.pos_between(pos, (0, 415), (64, 479)):
            self.highscore_page_idx = 0
            self.fetch_global_highscores = False
            self.fetch_local_highscores = False
            return {"screen": "main_menu", "play_sound": "click"}

        # then handle 'generic' click event
        self.highscore_page_idx += 1
        if self.highscore_page_idx >= 2:
            self.highscore_page_idx = 0
        return {"play_sound": "click"}
