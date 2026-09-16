# Main script
import pygame

import os
import random
import csv
from enum import Enum

from config import *
from entities import Electron, Positron, Player, Enemy, Arrow, PlayerState, HealthBar, Indicator
from menu import GameState, Menu


class GameDifficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


class EnemyTileMap():
    def __init__(self, file_name):
        self.file_name = file_name
        self.tile_size = TILE_SIZE
        self.map = []

    def load_csv(self):
        with open(os.path.join(DATA_DIR, self.file_name), newline="") as data:
            self.map = list(csv.reader(data))


# All sprites should go here to be moved when the camera moves
class CameraGroup(pygame.sprite.Group):
    def __init__(self, background):
        super().__init__()

        self.offset = pygame.math.Vector2(0, 0)
        self.background = background

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        self.screenshake = 0

    def shake(self, frames):
        self.screenshake = frames

    # Draw all sprites on screen w.r.t player
    def camera_draw(self, screen, player: Player):
        # Get offset
        self.offset.x = player.rect.x - self.screen_width / 2
        self.offset.y = player.rect.y - self.screen_height / 2

        # Draw background
        bg_width = self.background.get_width()
        bg_height = self.background.get_height()

        rand_x = 0
        rand_y = 0

        if self.screenshake:
            rand_x = random.randint(-SCREEN_SHAKE_MAGNITUDE, SCREEN_SHAKE_MAGNITUDE)
            rand_y = random.randint(-SCREEN_SHAKE_MAGNITUDE, SCREEN_SHAKE_MAGNITUDE)
            self.screenshake -= 1

        self.offset.x += rand_x
        self.offset.y += rand_y

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
        pygame.mixer.init()
        pygame.display.set_caption("TODO")

        # Play background music
        pygame.mixer.music.load(os.path.join(SOUND_DIR, "thesecondone.mp3"))
        pygame.mixer.music.set_volume(VOLUME)
        pygame.mixer.music.play(-1)

        # Clock for limiting FPS and screen to work with
        self.clock = pygame.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.mixer.music.pause()

        self.menu = Menu()

        # Background and screen
        self.bg_color = DARK_BLUE
        self.background = pygame.image.load(os.path.join(IMG_DIR, "background_with_particles.png")).convert_alpha()

        # Score stuff
        self.font = pygame.font.Font(SCORE_FONT, FONT_SIZE)
        self.score = 0

        # Enemy and player groups to know how we should apply attraction forces
        self.enemy_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

        # Elements that should move with the camera have to be added here 
        self.camera_group = CameraGroup(self.background)

        # Controllable electron player
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.reverse_enemy = None
        self.healthbar = HealthBar(HEALTHBAR_X, HEALTHBAR_Y)

        # Direction related
        self.angular_amplitude = STARTING_ANGULAR_AMPLITUDE # In degrees
        self.arrow = Arrow(PLAYER_START_X + 50, PLAYER_START_Y - 50, self.player.rect.centerx, self.player.rect.centery, self.angular_amplitude)
        self.indicator = Indicator(PLAYER_START_X, PLAYER_START_Y, self.angular_amplitude)

        # Tile map to load enemies
        self.difficulty_tilemaps : list[EnemyTileMap] = []
        self.difficulty_tilemaps_init()

        # Chunk related attributes
        self.chunk_size = ((self.difficulty_tilemaps[0].tile_size + TILE_PADDING) * len(self.difficulty_tilemaps[0].map[0]), 
                           (self.difficulty_tilemaps[0].tile_size + TILE_PADDING) * len(self.difficulty_tilemaps[0].map))
        self.chunk_y = self.chunk_size[1]
        self.loaded_chunk_columns = set()
        self.next_chunk_column = 0
        self.spawn_chunks(-1, 3)

        self.player_group.add(self.player)

        self.camera_group.add(self.indicator)
        self.camera_group.add(self.player)
        self.camera_group.add(self.arrow)

    def get_chunk_difficulty(self):
        # Should be between 1 and 0
        difficulty_factor = self.angular_amplitude / 180

        if difficulty_factor >= 2/3:
            return GameDifficulty.HARD
        elif difficulty_factor >= 1/3:
            return GameDifficulty.MEDIUM
        else:
            return GameDifficulty.EASY

    def difficulty_tilemaps_init(self):
        self.difficulty_tilemaps.append(EnemyTileMap("easy.csv"))
        self.difficulty_tilemaps.append(EnemyTileMap("medium.csv"))
        self.difficulty_tilemaps.append(EnemyTileMap("hard.csv"))

        self.difficulty_tilemaps[GameDifficulty.EASY.value].load_csv()
        self.difficulty_tilemaps[GameDifficulty.MEDIUM.value].load_csv()
        self.difficulty_tilemaps[GameDifficulty.HARD.value].load_csv()

    # Spawn a number of enemy chunks
    def spawn_chunks(self, first_column, count):
        cur_difficulty = self.get_chunk_difficulty()

        for column in range(first_column, first_column + count):
            if column in self.loaded_chunk_columns:
                continue

            self.spawn_enemy_chunk(column, cur_difficulty)
            self.loaded_chunk_columns.add(column)

            # Increase difficulty for next chunk
            cur_difficulty = GameDifficulty(min(GameDifficulty.HARD.value, cur_difficulty.value + 1))

        if first_column + count > self.next_chunk_column: self.next_chunk_column = first_column + count

    # For debugging
    def draw_position(self):
        pos_surface = self.font.render(f"({self.player.rect.x}, {self.player.rect.y})", False, FONT_COLOR)
        self.screen.blit(pos_surface, COORDINATE_POS)

    def draw_score(self):
        score_surface = self.font.render(str(self.score), False, FONT_COLOR)
        self.screen.blit(score_surface, SCORE_POS)

    def draw_dof(self):
        dof_surface = self.font.render("DoF: " + str(int(2 * self.angular_amplitude)) + "°", False, FONT_COLOR)
        self.screen.blit(dof_surface, DOF_POS)

    # Read CSV and spawn a single enemy chunk
    def spawn_enemy_chunk(self, column, difficulty : GameDifficulty):
        offset = pygame.math.Vector2(column * self.chunk_size[0], self.chunk_y)
        for row_idx, row in enumerate(self.difficulty_tilemaps[difficulty.value].map):
            for col_idx, value in enumerate(row):
                # Spawn enemy
                if value == "0":
                    new_enemy = Enemy((self.difficulty_tilemaps[difficulty.value].tile_size + TILE_PADDING) * col_idx + offset.x, (self.difficulty_tilemaps[difficulty.value].tile_size + TILE_PADDING) * row_idx + offset.y)

                    self.enemy_group.add(new_enemy)
                    self.camera_group.add(new_enemy)

    # Event handler
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if self.menu.state != GameState.PLAY:
                action = self.menu.handle_event(event)
                if action == "start" or action == "resume":
                    self.menu.state = GameState.PLAY
                    pygame.mixer.music.unpause()
                elif action == "retry":
                    self.reset_game()
                elif action == "quit":
                    pygame.quit()
                    raise SystemExit
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.menu.state = GameState.PAUSE
                pygame.mixer.music.pause()
                continue

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

    def reset_game(self):
        self.__init__()

        self.menu.state = GameState.PLAY
        pygame.mixer.music.unpause()

    def end_game(self):
        self.player.update_state(PlayerState.DEAD)
        
        self.menu.state = GameState.GAME_OVER
        pygame.mixer.music.pause()

    def rewind_player(self):
        current_pos = pygame.math.Vector2(self.player.rect.topleft)
        target_pos = self.player.last_pos
        reverse_offset = target_pos - current_pos

        if reverse_offset.length() <= REVERSE_VELOCITY:
            self.player.rect.topleft = (round(target_pos.x), round(target_pos.y))

            self.player.velocity = 0
            self.player.acceleration = 0
            self.player.angle = 0

            self.indicator.is_visible = True
            self.player.update_state(PlayerState.AIMING)
        else:
            self.player.rect.topleft = tuple(
                round(value) for value in current_pos + reverse_offset.normalize() * REVERSE_VELOCITY
            )

    def update_score(self):
        self.score = max(self.player.rect.centerx // 100, self.score)

    def update_angular_amplitude(self):
        if self.angular_amplitude < MAXIMUM_ANGULAR_AMPLITUDE: self.angular_amplitude += ANGLE_STEP

    def cleanup_enemies(self):
        # For keeping a few chunks ahead of the player and removing chunks well behind it.
        load_threshold = (self.next_chunk_column - 1) * self.chunk_size[0]
        if self.player.rect.right >= load_threshold:
            self.spawn_chunks(self.next_chunk_column, 3)

        cleanup_threshold = self.player.rect.left - self.chunk_size[0]

        for enemy in self.enemy_group:
            # Kill enemy far behind
            if enemy.rect.right < cleanup_threshold or not enemy.is_visible:
                enemy.kill()

    def handle_collision(self, enemy):
        if self.player.health - ENEMY_DAMAGE > 0:
            self.reverse_enemy = enemy
            self.player.update_state(PlayerState.REVERSING)

        self.angular_amplitude -= COLLISION_ANGLE_DEDUCTION
        if self.angular_amplitude < STARTING_ANGULAR_AMPLITUDE: self.angular_amplitude = STARTING_ANGULAR_AMPLITUDE

        self.indicator.is_visible = False
        self.arrow.is_visible = False

        self.player.health -= ENEMY_DAMAGE
        self.healthbar.count -= 1

    def check_collision(self):
        for enemy in self.enemy_group:
            collision = self.player.hitbox_rect.colliderect(enemy.hitbox_rect)
            
            if collision and not enemy.is_exploding: 
                self.handle_collision(enemy)
                enemy.explode()

    # Update entity states
    def update(self):
        if self.menu.state != GameState.PLAY: return

        # If player is dead
        if self.player.health <= 0:
            self.end_game()
            return

        # Upon a collision, reverse to previous position like a rewind. I've experimented with a normal repulsion force but the physics gets weird
        if self.player.state == PlayerState.REVERSING:
            self.rewind_player()

            # Screenshake while reversing
            self.camera_group.screenshake += 1

            # The reverse animation owns this frame; defer all other updates.
            return

        self.update_score()

        # Attraction forces
        for electron in self.player_group:
            for positron in self.enemy_group:
                electron.apply_attraction(positron) # Apply electron attraction to positron
                positron.apply_attraction(electron) # Apply positron attraction to electron

        # Angular amplitude
        self.update_angular_amplitude()

        # Update player
        for player in self.player_group:
            player.update()

            self.indicator.max_angular_amplitude = self.angular_amplitude
            self.indicator.update(player)

        # Update enemies
        for enemy in self.enemy_group:
            enemy.update()

        # Update arrow angle and visibility
        self.arrow.angular_amplitude = math.radians(self.angular_amplitude)
        self.arrow.update(self.player, self.camera_group.offset)
        
        if self.player.state == PlayerState.AIMING:
            self.arrow.is_visible = True
        else:
            self.arrow.is_visible = False

        # Cleanup and collisions
        self.cleanup_enemies()
        self.check_collision()
                    
    # Drawing handler
    def draw(self):
        # Draw sprites and background
        self.camera_group.camera_draw(self.screen, self.player)

        self.healthbar.draw(self.screen)
        self.draw_score()
        self.draw_dof()

    # Game loop
    def run(self):
        while True:
            self.handle_events()

            self.update()

            if self.menu.state == GameState.PLAY:
                self.draw()
            else:
                self.menu.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()