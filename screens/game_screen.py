from .screen import Screen
from pygame.image import load
import pygame


class GameScreen(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size

        # ingame parameters
        self.init = True
        self.score = 0

        # load the assets
        self.ready = load("assets/ready.png").convert_alpha()
        self.buttons = load("assets/buttons.png").convert_alpha()
        self.pausemenu = load("assets/pausemenu.png").convert_alpha()
        # load stains
        self.stains = [
            load("assets/stain1.png").convert_alpha(),
            load("assets/stain2.png").convert_alpha(),
            load("assets/stain3.png").convert_alpha(),
        ]
        # load heads
        self.headdown = load("assets/headdown.png").convert_alpha()
        self.headleft = load("assets/headleft.png").convert_alpha()
        self.headright = load("assets/headright.png").convert_alpha()
        self.headup = load("assets/headup.png").convert_alpha()

    def draw(self):
        Screen.draw(self)

        if self.init:
            self.pg_screen.blit(self.ready, (47, 100))

        self.draw_score()

        pygame.draw.line(self.pg_screen, (0, 0, 0), (0, 400), (319, 400))

        # draw the main menu
        # self.pg_screen.blit(self.logo, (5, 60))
        # self.pg_screen.blit(self.register_login, (150, 5))
        # self.pg_screen.blit(self.main_menu, (60, 250))
        # s = 64 - self.sound_on * 64
        # self.pg_screen.blit(self.buttons, (0, 415), (s, 0, 64, 64))
        # m = 64 - self.music_on * 64
        # self.pg_screen.blit(self.buttons, (64, 415), (m, 192, 64, 64))

    def draw_score(self):
        for digit in str(self.score):
            self.pg_screen.blit

    def update(self, events):
        Screen.update(self, events)

    def mouse_down(self, pos):
        if self.init:
            self.init = False
            return {"play_sound": "click"}
        return {"screen": "main_menu", "play_sound": "click"}

        # if self.pos_between(pos, (69, 258), (240, 287)):
        #    return {"screen": "game_screen", "play_sound": "click"}
        # elif self.pos_between(pos, (71, 301), (243, 330)):
        #    return {"screen": "highscores_screen", "play_sound": "click"}
        # elif self.pos_between(pos, (72, 345), (242, 379)):
        #    return {"screen": "help_screen", "play_sound": "click"}
        # elif self.pos_between(pos, (0, 415), (64, 479)):
        #    self.sound_on = not self.sound_on
        #    return {"sound": self.sound_on, "play_sound": "click"}
        # elif self.pos_between(pos, (64, 415), (128, 479)):
        #    self.music_on = not self.music_on
        #    return {"music": self.music_on, "play_sound": "click"}
