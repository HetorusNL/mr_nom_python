from .screen import Screen
from pygame.image import load
from pygame.font import Font
from utils import InputBox
from utils import Network


class RegisterScreen(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.network = Network()
        self.font = Font(None, 30)
        self.registering = False
        self.registering_status = None
        self.username = None

        # load the assets
        self.buttons = load("assets/buttons.png").convert_alpha()

        # create the input boxes
        self.username_box = InputBox((10, 90), (300, 40))
        self.password_box = InputBox((10, 170), (300, 40), type="password")
        self.email_box = InputBox((10, 250), (300, 40))

    def update(self, delta_time):
        if self.registering:
            print(self.network.get_register_status().status_code)
            registering_result = self.network.get_register_status()
            status_code = registering_result.status_code
            if status_code == 200:
                # successfully registered, show the user
                self.registering = False
                self.registering_status = [
                    f"{self.username}",
                    "Successfully registered!",
                    "You can login now...",
                ]
            elif status_code == 400:
                # invalid username/password/email supplied
                self.registering_status = [
                    "Invalid information supplied!",
                    "Username/password must have",
                    "5 characters or more,",
                    "email must be valid",
                ]
                self.registering = False
            elif status_code == 409:
                # username already exists
                self.registering_status = [
                    "Username already exists!",
                    "Try a different username",
                ]
                self.registering = False
            elif status_code != 0:
                # some unknown error occured
                self.registering_status = f"ERROR: status code: {status_code}"
                self.registering = False

    def draw(self):
        Screen.draw(self)

        self._draw_centered_text("Register to Mr Nom", (160, 30))
        self._draw_left_align_text("Username", (10, 60))
        self.username_box.draw(self.pg_screen)
        self._draw_left_align_text("Password", (10, 140))
        self.password_box.draw(self.pg_screen)
        self._draw_left_align_text("Email", (10, 220))
        self.email_box.draw(self.pg_screen)
        self._draw_centered_text("REGISTER", (160, 330))

        self.pg_screen.blit(self.buttons, (0, 415), (64, 64, 64, 64))

        # draw text last, so it overlaps everything (if overlapping happens)
        if self.registering_status:
            if type(self.registering_status) == list:
                offset = 370
                for line in self.registering_status:
                    self._draw_centered_text(line, (160, offset))
                    offset += 25
            else:  # string
                self._draw_centered_text(self.registering_status, (160, 370))

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
            self.reset()
            return {"screen": "main_menu", "play_sound": "click"}
        elif self.pos_between(pos, (100, 311), (220, 339)):
            if not self.registering:
                # set the screen properties
                self.registering = True
                self.registering_status = "Registering..."
                self.username = self.username_box.text
                print("registering...")

                # send registering request
                username = self.username_box.text
                password = self.password_box.text
                email = self.email_box.text
                self.network.perform_register(username, password, email)

    def key_press(self, event):
        self.username_box.key_press(event)
        self.password_box.key_press(event)
        self.email_box.key_press(event)

    def reset(self):
        self.username_box.reset()
        self.password_box.reset()
        self.email_box.reset()
        self.registering = False
        self.registering_status = None
