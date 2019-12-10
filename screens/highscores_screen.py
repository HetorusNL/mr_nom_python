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
        self.fetch_personal_highscores = True
        self.global_highscores_page = 0
        self.personal_highscores_page = 0
        self.highscore_page_idx = 0

        # load the assets
        self.mainmenu = load("assets/mainmenu.png").convert_alpha()
        self.numbers = load("assets/numbers.png").convert_alpha()
        self.buttons = load("assets/buttons.png").convert_alpha()

    def update(self, delta_time):
        if self.highscore_page_idx == 0 and self.fetch_global_highscores:
            self.fetch_global_highscores = False
            result = self.network.fetch_global_highscores()
            if not result["result"]:
                print(result["status"])
            print(result)

        if self.highscore_page_idx == 1 and self.fetch_personal_highscores:
            self.fetch_personal_highscores = False
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
                self._draw_global_highscores()
            elif self.network.get_global_highscores().status_code != 0:
                self._draw_failed_highscore_fetch("global")
        elif self.highscore_page_idx == 1:
            if self.network.get_local_highscores().status_code == 200:
                self._draw_personal_highscorees()
            elif self.network.get_local_highscores().status_code != 0:
                self._draw_failed_highscore_fetch("personal", "not logged in!")

        # notify user that there is another highscores page
        self._draw_centered_text("Click highscores page for", (190, 430))
        which = "PERSONAL" if self.highscore_page_idx == 0 else "GLOBAL"
        self._draw_centered_text(f"{which} highscores", (190, 460))

        self.pg_screen.blit(self.buttons, (0, 415), (64, 64, 64, 64))

    def _draw_failed_highscore_fetch(self, which, second=None):
        self._draw_centered_text("failed to get", (160, 85))
        self._draw_centered_text("{} highscores!".format(which), (160, 110))

        if second:
            self._draw_centered_text(second, (160, 240))

    def _draw_global_highscores(self):
        # draw the titles of the highscore columns
        color = (150, 150, 150)
        self._draw_left_align_text("Username", (10, 70), color)
        self._draw_left_align_text("Score", (150, 70), color)
        self._draw_left_align_text("Time", (240, 70), color)

        # draw up to 5 of the highscores themselves
        highscores = self.network.get_global_highscores().data
        highscores_length = len(highscores) - 5 * self.global_highscores_page
        for i in range(5 if highscores_length > 5 else highscores_length):
            highscore = highscores[i + 5 * self.global_highscores_page]
            self._draw_left_align_text(highscore["user"], (10, 110 + i * 45))
            self._draw_numbers(highscore["score"], (150, 100 + i * 45))
            self._draw_numbers(highscore["time"] // 1000, (240, 100 + i * 45))

        # draw pagination stuff
        self.pg_screen.blit(self.buttons, (32, 330), (64, 64, 64, 64))
        self.pg_screen.blit(self.buttons, (224, 330), (0, 64, 64, 64))
        num_pages = len(highscores) // 5 + 1 if len(highscores) > 0 else 0
        page_string = f"page {self.global_highscores_page+1} / {num_pages}"
        self._draw_centered_text(page_string, (160, 362))

    def _draw_numbers(self, numbers, left_top):
        numbers_length = len(str(numbers))
        for i in range(numbers_length):
            x_offset = left_top[0] + i * 20
            x_index = 20 * int(str(numbers)[i])
            self.pg_screen.blit(
                self.numbers, (x_offset, left_top[1]), (x_index, 0, 20, 32)
            )

    def _draw_centered_text(self, text, center_coord, color=(0, 0, 0)):
        text = self.font.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.center = center_coord
        self.pg_screen.blit(text, text_rect)

    def _draw_left_align_text(self, text, top_left, color=(0, 0, 0)):
        text = self.font.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.topleft = top_left
        self.pg_screen.blit(text, text_rect)

    def mouse_down(self, pos):
        # first handle specific position
        if self.pos_between(pos, (0, 415), (64, 479)):
            self.highscore_page_idx = 0
            self.fetch_global_highscores = True
            self.fetch_personal_highscores = True
            return {"screen": "main_menu", "play_sound": "click"}

        # if the function processes the position, return its result
        result = self._check_highscore_pagination(pos)
        if result:
            return result

        # then handle 'generic' click event
        self.highscore_page_idx += 1
        if self.highscore_page_idx >= 2:
            self.highscore_page_idx = 0
        return {"play_sound": "click"}

    def _check_highscore_pagination(self, pos):
        # check which highscore page is shown, decrement page if possible
        if self.pos_between(pos, (32, 330), (96, 394)):
            if self.highscore_page_idx == 0:
                if self.global_highscores_page > 0:
                    self.global_highscores_page -= 1
                return {"play_sound": "click"}
            elif self.highscore_page_idx == 1:
                if self.personal_highscores_page > 0:
                    self.personal_highscores_page -= 1
                return {"play_sound": "click"}
        # check which highscore page, valid network response and can increment
        elif self.pos_between(pos, (224, 330), (288, 394)):
            if self.highscore_page_idx == 0:
                if self.network.get_global_highscores().status_code == 200:
                    length = len(self.network.get_global_highscores().data)
                    num_pages = length // 5 + 1 if length > 0 else 0
                    if self.global_highscores_page < num_pages - 1:
                        self.global_highscores_page += 1
                return {"play_sound": "click"}
            elif self.highscore_page_idx == 1:
                if self.network.get_local_highscores().status_code == 200:
                    length = len(self.network.get_local_highscores().data)
                    num_pages = length // 5 + 1 if length > 0 else 0
                    if self.personal_highscores_page < num_pages - 1:
                        self.personal_highscores_page += 1
                return {"play_sound": "click"}
