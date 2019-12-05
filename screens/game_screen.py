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
        self.pause = False
        self.score = 0
        self.direction = 0  # [0,1,2,3] == [up,right,down,left]
        self.snake = [(5, 5), (5, 6), (5, 7)]  # 10 * 13 squares

        # load the assets
        self.ready = load("assets/ready.png").convert_alpha()
        self.buttons = load("assets/buttons.png").convert_alpha()
        self.pausemenu = load("assets/pausemenu.png").convert_alpha()
        self.numbers = load("assets/numbers.png").convert_alpha()
        self.tail = load("assets/tail.png").convert_alpha()
        # load stains
        self.stains = [
            load("assets/stain1.png").convert_alpha(),
            load("assets/stain2.png").convert_alpha(),
            load("assets/stain3.png").convert_alpha(),
        ]
        # load heads
        self.heads = [
            load("assets/headup.png").convert_alpha(),
            load("assets/headright.png").convert_alpha(),
            load("assets/headdown.png").convert_alpha(),
            load("assets/headleft.png").convert_alpha(),
        ]

    def draw(self):
        Screen.draw(self)

        self.draw_score()
        pygame.draw.line(self.pg_screen, (0, 0, 0), (0, 415), (319, 415))
        self.draw_snake()

        if self.init:
            self.pg_screen.blit(self.ready, (47, 100))
            return

        if self.pause:
            self.pg_screen.blit(self.pausemenu, (80, 100))
        else:
            self.pg_screen.blit(self.buttons, (0, 0), (64, 128, 64, 64))
            self.pg_screen.blit(self.buttons, (0, 415), (64, 64, 64, 64))
            self.pg_screen.blit(self.buttons, (256, 415), (0, 64, 64, 64))

        # draw the main menu
        # self.pg_screen.blit(self.logo, (5, 60))
        # self.pg_screen.blit(self.register_login, (150, 5))
        # self.pg_screen.blit(self.main_menu, (60, 250))
        # s = 64 - self.sound_on * 64
        # self.pg_screen.blit(self.buttons, (0, 415), (s, 0, 64, 64))
        # m = 64 - self.music_on * 64
        # self.pg_screen.blit(self.buttons, (64, 415), (m, 192, 64, 64))

    def draw_score(self):
        score_length = len(str(self.score))
        for i in range(score_length):
            x_offset = 160 - score_length * 10 + i * 20
            x_index = 20 * int(str(self.score)[i])
            self.pg_screen.blit(
                self.numbers, (x_offset, 420), (x_index, 0, 20, 32)
            )

    def draw_snake(self):
        # draw the tail
        for tail in self.snake[1:]:
            self.pg_screen.blit(self.tail, (tail[0] * 32, tail[1] * 32))

        # draw the head (on top)
        self.pg_screen.blit(
            self.heads[self.direction],
            (self.snake[0][0] * 32 - 5, self.snake[0][1] * 32 - 5),
        )

    def update(self, events):
        Screen.update(self, events)

    def reset(self):
        self.init = True
        self.pause = False
        self.direction = 0
        self.snake = [(5, 5), (5, 6), (5, 7)]
        self.score = 0

    def mouse_down(self, pos):
        if self.init:
            self.init = False
            return {"play_sound": "click"}

        if self.pause:
            if self.pos_between(pos, (83, 100), (232, 142)):
                self.pause = False
                return {"play_sound": "click"}
            elif self.pos_between(pos, (90, 151), (233, 190)):
                self.reset()
                return {"screen": "main_menu", "play_sound": "click"}
        else:  # playing
            if self.pos_between(pos, (0, 0), (64, 64)):
                self.pause = True
                return {"play_sound": "click"}
            if self.pos_between(pos, (0, 415), (64, 479)):
                self.direction = (self.direction - 1) % 4
                return {"play_sound": "click"}
            if self.pos_between(pos, (256, 415), (320, 479)):
                self.direction = (self.direction + 1) % 4
                return {"play_sound": "click"}

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
