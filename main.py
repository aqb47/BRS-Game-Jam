# Main script
import pygame
from config import *
from entities import Electron, Positron, Player, Enemy, Arrow, PlayerState

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

        # Controllable electron player
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)

        # Placeholders, we'll add automatic enemy generation later
        self.enemy1 = Enemy(PLAYER_START_X + 100, PLAYER_START_Y + 200)
        self.enemy2 = Enemy(PLAYER_START_X + 100, PLAYER_START_Y - 200)
        self.enemy3 = Enemy(PLAYER_START_X + 500, PLAYER_START_Y - 150)

        # Arrow for direction
        self.arrow = Arrow(PLAYER_START_X + 50, PLAYER_START_Y - 50, self.player.rect.centerx, self.player.rect.centery, 180)

        self.player_group.add(self.player)
        self.enemy_group.add(self.enemy1, self.enemy2, self.enemy3)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Shoot electron
                if event.button == 1: # Left click
                    if self.player.state == PlayerState.AIMING:
                        self.player.move(self.arrow.angle)

            if event.type == pygame.KEYDOWN:
                # Apply resistive force
                if event.key == pygame.K_SPACE:
                    if self.player.state == PlayerState.MOVING:
                        self.player.apply_friction()


        # Mouse position for arrow
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.arrow.mouse_pos = (mouse_x, mouse_y)

    # Update entity states
    def update(self):
        for electron in self.player_group:
            for positron in self.enemy_group:
                electron.apply_attraction(positron) # Apply electron attraction to positron
                positron.apply_attraction(electron) # Apply positron attraction to electron

        for player in self.player_group:
            player.update()

        for enemy in self.enemy_group:
            enemy.update()

        self.arrow.update(self.player)

    # Draw them on the screen
    def draw(self):
        # fill with background color
        self.screen.fill(self.bg_color)

        for player in self.player_group:
            player.draw(self.screen)

        for enemy in self.enemy_group:
            enemy.draw(self.screen)

        if player.state == PlayerState.AIMING:
            self.arrow.draw(self.screen)

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