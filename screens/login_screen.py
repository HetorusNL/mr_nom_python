from .screen import Screen
from pygame.image import load
from pygame.font import Font
from utils import InputBox
from utils import Network


class LoginScreen(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.network = Network()
        self.font = Font(None, 30)
        self.logging_in = False
        self.logging_in_status = None
        self.username = None

        # load the assets
        self.buttons = load("assets/buttons.png").convert_alpha()

        # create the input boxes
        self.username_box = InputBox((10, 150), (300, 40))
        self.password_box = InputBox((10, 230), (300, 40), type="password")

    def update(self, delta_time):
        if self.logging_in:
            print(self.network.get_login_result().status_code)
            logging_in_result = self.network.get_login_result()
            status_code = logging_in_result.status_code
            if status_code == 200:
                # put the access_token and username in the network _cache
                access_token = logging_in_result.data.get("access_token")
                self.network._cache["access_token"] = access_token
                self.network._cache["username"] = self.username
                self.logging_in = False
                self.logging_in_status = [
                    f"{self.username}",
                    "Successfully logged in!",
                ]
            elif status_code == 401:
                # non-existing user supplied
                self.logging_in_status = [
                    "Supplied username and",
                    "password not found!",
                ]
                self.logging_in = False
            elif status_code != 0:
                # some unknown error occured
                self.logging_in_status = f"ERROR: status code: {status_code}"
                self.logging_in = False

    def draw(self):
        Screen.draw(self)

        self._draw_centered_text("Login to Mr Nom", (160, 60))
        self._draw_left_align_text("Username", (10, 120))
        self.username_box.draw(self.pg_screen)
        self._draw_left_align_text("Password", (10, 200))
        self.password_box.draw(self.pg_screen)
        self._draw_centered_text("LOGIN", (160, 310))

        if self.logging_in_status:
            if type(self.logging_in_status) == list:
                offset = 350
                for line in self.logging_in_status:
                    self._draw_centered_text(line, (160, offset))
                    offset += 25
            else:  # string
                self._draw_centered_text(self.logging_in_status, (160, 350))

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

        if self.pos_between(pos, (0, 415), (64, 479)):
            self.reset()
            return {"screen": "main_menu", "play_sound": "click"}
        elif self.pos_between(pos, (120, 291), (201, 320)):
            if not self.logging_in:
                # set the screen properties
                self.logging_in = True
                self.logging_in_status = "Logging in..."
                self.username = self.username_box.text
                print("logging in...")

                # send login request
                username = self.username_box.text
                password = self.password_box.text
                self.network.perform_login(username, password)

    def key_press(self, event):
        self.username_box.key_press(event)
        self.password_box.key_press(event)

    def reset(self):
        self.username_box.reset()
        self.password_box.reset()
        self.logging_in = False
        self.logging_in_status = False
