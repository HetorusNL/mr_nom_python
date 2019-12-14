from pygame.image import load


class Screen(object):
    def __init__(self, pg_screen, screen_size):
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.background = load("assets/background.png").convert()

    def draw(self):
        self.pg_screen.blit(self.background, (0, 0))

    def update(self, delta_time):
        return None

    def mouse_down(self, pos):
        pass

    def key_press(self, event):
        pass

    def pos_between(self, pos, top_left, bot_right):
        return (pos[0] >= top_left[0] and pos[0] <= bot_right[0]) and (
            pos[1] >= top_left[1] and pos[1] <= bot_right[1]
        )
