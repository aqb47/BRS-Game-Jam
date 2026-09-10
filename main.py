# Main script
import pygame
from config import *
from entities import Electron, Positron, Player, Enemy

# This'll tie everything together basically
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TODO")

        self.clock = pygame.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.bg_color = BG

        self.particle_group = pygame.sprite.Group()

        self.enemy_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.enemy1 = Enemy(PLAYER_START_X + 100, PLAYER_START_Y + 200)
        self.enemy2 = Enemy(PLAYER_START_X + 100, PLAYER_START_Y - 200)

        self.player_group.add(self.player)
        self.enemy_group.add(self.enemy1, self.enemy2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

    # Update entity states
    def update(self):
        for player in self.player_group:
            player.update()

    # Draw them on the screen
    def draw(self):
        # fill with background color
        self.screen.fill(self.bg_color)

        for player in self.player_group:
            player.draw(self.screen)

        for enemy in self.enemy_group:
            enemy.draw(self.screen)


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