from enum import Enum
import pygame

from config import *

class GameState(Enum):
    START = 0
    PLAY = 1
    PAUSE = 2
    GAME_OVER = 3


class Menu():
    TITLE_TEXT = "- SubElectronic -"

    def __init__(self):
        self.state = GameState.START

        self.selected_index = 0

        self.title_font = pygame.font.Font(TITLE_FONT, 70)
        self.menu_font = pygame.font.Font(FONT, 35)
        self.heading_font = pygame.font.Font(TITLE_FONT, 60)

        self.title_font.set_bold(True)
        self.heading_font.set_bold(True)

        self.score = 0

    @property
    def options(self):
        if self.state == GameState.START:
            return ("Start", "Quit")
        if self.state == GameState.GAME_OVER:
            return ("Retry", "Quit")
        return ("Resume", "Quit")

    # Handle a keydown event from pygame.events.get()
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # Move up one index, wrap around circularly
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (self.selected_index - 1) % len(self.options)

        # Move down one index, wrap around circularly
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (self.selected_index + 1) % len(self.options)

        # Select an option
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return self.options[self.selected_index].lower()

        # Hitting 'esc' on pause menu
        elif event.key == pygame.K_ESCAPE and self.state == GameState.PAUSE:
            return "resume"

        return None

    def draw(self, screen):
        screen.fill(BLACK)

        if self.state == GameState.START:
            title = self.title_font.render(self.TITLE_TEXT, True, LIGHT_TURQUOISE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(title, title_rect)
        else:
            heading_text = "PAUSED" if self.state == GameState.PAUSE else f"GAME OVER\n       {self.score}"
            heading = self.heading_font.render(heading_text, True, LIGHT_TURQUOISE)
            heading_rect = heading.get_rect(center=(SCREEN_WIDTH // 1.9, SCREEN_HEIGHT // 3))
            screen.blit(heading, heading_rect)

        option_surfaces = []
        for index, option in enumerate(self.options):
            color = LIGHT_TURQUOISE if index == self.selected_index else FONT_COLOR
            prefix = "> " if index == self.selected_index else "  "
            option_surfaces.append(self.menu_font.render(prefix + option, True, color))

        total_height = sum(surface.get_height() for surface in option_surfaces)
        y_position = (SCREEN_HEIGHT + SCREEN_HEIGHT // 3 - total_height) // 2
        for surface in option_surfaces:
            rect = surface.get_rect(centerx=SCREEN_WIDTH // 2, top=y_position)
            screen.blit(surface, rect)
            y_position += surface.get_height()