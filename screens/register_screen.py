from .screen import Screen
from pygame.image import load
from pygame.font import Font
from utils import InputBox


class RegisterScreen(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.font = Font(None, 30)

        # load the assets
        self.buttons = load("assets/buttons.png").convert_alpha()

        # create the input boxes
        self.username_box = InputBox((10, 150), (300, 40))
        self.password_box = InputBox((10, 230), (300, 40), type="password")
        self.email_box = InputBox((10, 310), (300, 40))

    def draw(self):
        Screen.draw(self)

        self._draw_centered_text("Register to Mr Nom", (160, 60))
        self._draw_left_align_text("Username", (10, 120))
        self.username_box.draw(self.pg_screen)
        self._draw_left_align_text("Password", (10, 200))
        self.password_box.draw(self.pg_screen)
        self._draw_left_align_text("Email", (10, 280))
        self.email_box.draw(self.pg_screen)
        self._draw_centered_text("REGISTER", (160, 390))

        self.pg_screen.blit(self.buttons, (0, 415), (64, 64, 64, 64))

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
        self.username_box.mouse_down(pos)
        self.password_box.mouse_down(pos)
        self.email_box.mouse_down(pos)

        if self.pos_between(pos, (0, 415), (64, 479)):
            self.username_box.reset()
            self.password_box.reset()
            self.email_box.reset()
            return {"screen": "main_menu", "play_sound": "click"}
        elif self.pos_between(pos, (100, 371), (220, 399)):
            print("registering...")

    def key_press(self, event):
        self.username_box.key_press(event)
        self.password_box.key_press(event)
        self.email_box.key_press(event)
