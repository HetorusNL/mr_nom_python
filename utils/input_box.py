import pygame
from pygame.font import Font


class InputBox:
    def __init__(self, left_top, width_height, text="", type="text"):
        self.color_inactive = pygame.Color("lightskyblue3")
        self.color_active = pygame.Color("dodgerblue2")
        self.rect = pygame.Rect(left_top, width_height)
        self.color = self.color_inactive
        self.text = text
        self.type = type
        self.font = Font(None, 30)
        if self.type == "password":
            self.txt_surface = self.font.render(
                "*" * len(text), True, self.color
            )
        else:  # defaults to text
            self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 3)

    def mouse_down(self, pos):
        if self.rect.collidepoint(pos):
            # Toggle the active variable.
            self.active = not self.active
        else:
            self.active = False
        # Change the current color of the input box.
        self.color = self.color_active if self.active else self.color_inactive

    def key_press(self, event):
        if self.active:
            if event.key == pygame.K_RETURN:
                print(self.text)
                self.text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            # Re-render the text.
            if self.type == "password":
                self.txt_surface = self.font.render(
                    "*" * len(self.text), True, self.color
                )
            else:  # defaults to text
                self.txt_surface = self.font.render(
                    self.text, True, self.color
                )

    def reset(self):
        self.text = ""
        if self.type == "password":
            self.txt_surface = self.font.render(
                "*" * len(self.text), True, self.color
            )
        else:  # defaults to text
            self.txt_surface = self.font.render(self.text, True, self.color)
