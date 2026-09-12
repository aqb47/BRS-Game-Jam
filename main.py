# Main script
import pygame

import os
import random
import csv

from config import *
from entities import Electron, Positron, Player, Enemy, Arrow, PlayerState


class EnemyTileMap():
    map = [[]]

    def __init__(self, file_name):
        self.file_name = file_name
        self.tile_size = ENEMY_TILE_SIZE

    def load_csv(self):
        with open(os.path.join(DATA_DIR, self.file_name)) as data:
            EnemyTileMap.map = list(csv.reader(data))


# All sprites should go here to be moved when the camera moves
class CameraGroup(pygame.sprite.Group):
    def __init__(self, background):
        super().__init__()

        self.offset = pygame.math.Vector2(0, 0)
        self.background = background

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

    # Draw all sprites on screen w.r.t player
    def camera_draw(self, screen, player: Player):
        # Get offset
        self.offset.x = player.rect.x - self.screen_width / 2
        self.offset.y = player.rect.y - self.screen_height / 2

        # Draw background
        bg_width = self.background.get_width()
        bg_height = self.background.get_height()

        start_x = int(-self.offset.x % bg_width - bg_width)
        start_y = int(-self.offset.y % bg_height - bg_height)

        for x in range(start_x, self.screen_width, bg_width):
            for y in range(start_y, self.screen_height, bg_height):
                screen.blit(self.background, (x, y))

        # Draw sprites
        for sprite in self.sprites():
            # If a sprite is currently invisible
            if hasattr(sprite, "is_visible") and not sprite.is_visible: continue

            screen.blit(sprite.image, sprite.rect.topleft - self.offset)


# This'll tie everything together basically
class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("TODO")

        # Clock for limiting FPS and screen to work with
        self.clock = pygame.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Background
        self.bg_color = BG
        self.background = pygame.image.load(os.path.join(IMG_DIR, "sample_background.png")).convert_alpha()

        # Score stuff
        self.font = pygame.font.Font(SCORE_FONT, SCORE_FONT_SIZE)
        self.score = 0

        # Enemy and player groups to know how we should apply attraction forces
        self.enemy_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

        # Elements that should move with the camera have to be added here 
        self.camera_group = CameraGroup(self.background)

        # Controllable electron player
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)

        # track when we spawned enemies last
        self.last_enemy_spawn_time = 0

        # Arrow for direction
        self.arrow = Arrow(PLAYER_START_X + 50, PLAYER_START_Y - 50, self.player.rect.centerx, self.player.rect.centery, 180)

        # Tile map to load enemies
        self.tilemap = EnemyTileMap("example.csv")
        self.tilemap.load_csv()
        self.spawn_enemies()

        self.player_group.add(self.player)

        self.camera_group.add(self.player)
        self.camera_group.add(self.arrow)

    def draw_score(self):
        score_surface = self.font.render(str(self.score), False, SCORE_COLOR)
        self.screen.blit(score_surface, SCORE_POS)

    def spawn_enemies(self):
        for row_idx, row in enumerate(self.tilemap.map):
            for col_idx, value in enumerate(row):
                # Spawn enemy
                if value == "0":
                    new_enemy = Enemy((self.tilemap.tile_size + TILE_PADDING) * col_idx, (self.tilemap.tile_size + TILE_PADDING) * row_idx)

                    self.enemy_group.add(new_enemy)
                    self.camera_group.add(new_enemy)

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
        # basic scoring for now
        self.score = self.player.rect.centerx

        # Attraction forces
        for electron in self.player_group:
            for positron in self.enemy_group:
                electron.apply_attraction(positron) # Apply electron attraction to positron
                positron.apply_attraction(electron) # Apply positron attraction to electron

        for player in self.player_group:
            player.update()

        for enemy in self.enemy_group:
            enemy.update()

        # Update arrow angle and visibility
        self.arrow.update(self.player, self.camera_group.offset)
        
        if self.player.state == PlayerState.AIMING:
            self.arrow.is_visible = True
        else:
            self.arrow.is_visible = False

    # Draw them on the screen
    def draw(self):
        # fill with background color
        self.screen.fill(self.bg_color)

        # Draw sprites and background
        self.camera_group.camera_draw(self.screen, self.player)

        self.draw_score()

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