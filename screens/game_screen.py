from .screen import Screen
from utils import Network
from pygame.image import load
from pygame.font import Font
import pygame
import random


class GameScreen(Screen):
    def __init__(self, pg_screen, screen_size):
        Screen.__init__(self, pg_screen, screen_size)
        self.pg_screen = pg_screen
        self.screen_size = screen_size
        self.network = Network()
        self.font = Font(None, 30)
        self.arrow_keys = {
            pygame.K_UP: 0,
            pygame.K_w: 0,
            pygame.K_LEFT: 1,
            pygame.K_a: 1,
            pygame.K_DOWN: 2,
            pygame.K_s: 2,
            pygame.K_RIGHT: 3,
            pygame.K_d: 3,
        }

        # ingame parameters
        self.init = True
        self.pause = False
        self.score = 0
        self.game_over = False
        self.game_time = 0
        self.game_tick = 0.5
        self.game_tick_decrement = 0.05
        self.direction = 0  # [0,1,2,3] == [up,left,down,right]
        self.snake = [(5, 5), (5, 6), (5, 7)]  # 10 * 13 squares
        self.stain_pos = self._generate_stain_pos()

        # load the assets
        self.ready = load("assets/ready.png").convert_alpha()
        self.gameover = load("assets/gameover.png").convert_alpha()
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
            load("assets/headleft.png").convert_alpha(),
            load("assets/headdown.png").convert_alpha(),
            load("assets/headright.png").convert_alpha(),
        ]
        self.stain = random.choice(self.stains)

    def update(self, delta_time):
        Screen.update(self, delta_time)

        if self.game_over or self.pause or self.init:
            return

        # calculate game loop updates
        self.game_time += delta_time
        results = {}

        while self.game_time >= self.game_tick:
            print("evaluate tick after tick_time:", self.game_tick)
            self.game_time -= self.game_tick

            # move the snake to the new position
            old_head = self.snake[0]
            new_head = (0, 0)
            if self.direction == 0:
                new_head = (old_head[0], (old_head[1] - 1) % 13)
            elif self.direction == 1:
                new_head = ((old_head[0] - 1) % 10, old_head[1])
            elif self.direction == 2:
                new_head = (old_head[0], (old_head[1] + 1) % 13)
            elif self.direction == 3:
                new_head = ((old_head[0] + 1) % 10, old_head[1])
            self.snake = self.snake[:-1]
            self.snake.insert(0, new_head)

            # check for collision
            for tail in self.snake[1:]:
                if self.snake[0] == tail:
                    self.game_over = True
                    results["play_sound"] = "bitten"

            # check for stain
            if self.snake[0] == self.stain_pos:
                # snake add stain, increment score, add new stain, etc
                results["play_sound"] = "eat"
                self.score += 10
                if self.score % 100 == 0:
                    if self.game_tick > self.game_tick_decrement:
                        self.game_tick -= self.game_tick_decrement
                    else:
                        print("can't go any faster!")
                self.snake.append(self.snake[-1])
                if len(self.snake) != 130:
                    self.stain = random.choice(self.stains)
                    self.stain_pos = self._generate_stain_pos()
                else:
                    self.game_over = True

        return results

    def draw(self):
        Screen.draw(self)

        self.draw_score()
        pygame.draw.line(self.pg_screen, (0, 0, 0), (0, 415), (319, 415))
        self.draw_snake()
        self.pg_screen.blit(
            self.stain, (self.stain_pos[0] * 32, self.stain_pos[1] * 32)
        )

        if self.init:
            self.pg_screen.blit(self.ready, (47, 100))
            # if user is logged in, display their name
            username = self.network._cache["username"]
            line1 = "Logged in as:" if username else "Not logged in!"
            line2 = username if username else "Highscore won't be submitted"
            self._draw_centered_text(line1, (160, 50))
            self._draw_centered_text(line2, (160, 75))
            return

        if self.game_over:
            self.pg_screen.blit(self.gameover, (47, 100))
            self.pg_screen.blit(self.buttons, (128, 208), (0, 128, 64, 64))
            return

        if self.pause:
            self.pg_screen.blit(self.pausemenu, (80, 100))
        else:
            self.pg_screen.blit(self.buttons, (0, 0), (64, 128, 64, 64))
            self.pg_screen.blit(self.buttons, (0, 415), (64, 64, 64, 64))
            self.pg_screen.blit(self.buttons, (256, 415), (0, 64, 64, 64))

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
        if self.init:
            self.init = False
            return {"play_sound": "click"}

        if self.game_over:
            if self.pos_between(pos, (128, 208), (192, 272)):
                self.reset()
                return {"screen": "main_menu", "play_sound": "click"}

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
                self.direction = (self.direction + 1) % 4
                return {"play_sound": "click"}
            if self.pos_between(pos, (256, 415), (320, 479)):
                self.direction = (self.direction - 1) % 4
                return {"play_sound": "click"}

    def key_press(self, event):
        if self.init or self.pause or self.game_over:
            return

        # user is playing, handle key press
        if event.key in self.arrow_keys.keys():
            self.direction = self.arrow_keys[event.key]

    def _generate_stain_pos(self):
        new_stain = (random.randint(0, 9), random.randint(0, 12))
        for y in range(13):
            for x in range(10):
                _new_stain = ((new_stain[0] + x) % 10, (new_stain[1] + y) % 13)
                if _new_stain not in self.snake:
                    print(_new_stain)
                    return _new_stain

    def reset(self):
        self.init = True
        self.pause = False
        self.game_over = False
        self.direction = 0
        self.snake = [(5, 5), (5, 6), (5, 7)]
        self.score = 0
        self.game_time = 0
        self.game_tick = 0.5
        self.stain_pos = self._generate_stain_pos()
