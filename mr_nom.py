import pygame
import sys
import time

from screens import GameScreen, HelpScreen, HighscoresScreen, MainMenu
from utils import Audio

pygame.mixer.init(buffer=512)
pygame.init()


class MrNom(object):
    def __init__(self):
        # initialize the game parameters
        screen_width = 320
        screen_height = 480
        screen_size = (screen_width, screen_height)
        pg_screen = pygame.display.set_mode((screen_width, screen_height))
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

        # initialize the screens
        self.screens = {
            "game_screen": GameScreen(pg_screen, screen_size),
            "help_screen": HelpScreen(pg_screen, screen_size),
            "highscores_screen": HighscoresScreen(pg_screen, screen_size),
            "main_menu": MainMenu(pg_screen, screen_size),
        }
        self.screen = "main_menu"
        self.audio = Audio()
        self.audio.set_music(self.screens["main_menu"].music_on)
        self.audio.set_sound(self.screens["main_menu"].sound_on)

        self.game_time = time.time()

        # run the game loop forever
        while True:
            self.game_loop()

    def game_loop(self):
        results = {}

        # process timing stuff
        current_time = time.time()
        time_delta = current_time - self.game_time
        self.game_time = current_time

        # process the event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                print("shutting down...")
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
                mouse_results = self.screens[self.screen].mouse_down(pos)
                if mouse_results:
                    results = {**results, **mouse_results}
            elif (
                event.type == pygame.KEYDOWN
                and event.key in self.arrow_keys.keys()
            ):
                self.screens[self.screen].key_press(self.arrow_keys[event.key])

        # call update on the screen, and add results if present
        update_results = self.screens[self.screen].update(time_delta)
        if update_results:
            results = {**results, **update_results}

        if results.get("screen") is not None:
            self.screen = results.get("screen")

        if results.get("music") is not None:
            self.audio.set_music(results["music"])
        if results.get("sound") is not None:
            self.audio.set_sound(results["sound"])
        if results.get("play_sound") is not None:
            self.audio.play_sound(results["play_sound"])

        self.screens[self.screen].draw()

        pygame.display.update()
        pygame.time.delay(30)  # ~30fps


if __name__ == "__main__":
    # start the main function if this script is executed
    MrNom()
