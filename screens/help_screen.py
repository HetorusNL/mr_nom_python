from .screen import Screen
from pygame.image import load


class HelpScreen(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.help_page_idx = 0

        # load the assets
        self.help_pages = [
            load("assets/help1.png").convert_alpha(),
            load("assets/help2.png").convert_alpha(),
            load("assets/help3.png").convert_alpha(),
        ]
        self.buttons = load("assets/buttons.png").convert_alpha()

    def draw(self):
        Screen.draw(self)

        # draw the current help screen
        self.pg_screen.blit(self.help_pages[self.help_page_idx], (46, 112))
        self.pg_screen.blit(self.buttons, (256, 415), (0, 64, 64, 128))

    def update(self, events):
        Screen.update(self, events)

    def mouse_down(self, pos):
        self.help_page_idx += 1
        if self.help_page_idx >= 3:
            self.help_page_idx = 0
            return {"screen": "main_menu", "play_sound": "click"}
        return {"play_sound": "click"}
