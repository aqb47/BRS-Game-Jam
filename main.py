# Main script
import pygame
from config import *

# This'll tie everything together basically
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TODO")

        self.clock = pygame.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

    # Update entity states
    def update(self):
        pass

    # Draw them on the screen
    def draw(self):
        pass

    # Game loop
    def run(self):
        while True:
            self.handle_events()

            self.update()

            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()