import pygame
from config import *
import os

class Particle(pygame.sprite.Sprite):
    def __init__(self, charge, mass, vibration_velocity):
        super().__init__()
        self.charge = charge
        self.mass = mass

        self.position = 0
        self.angle = 0

        self.velocity = 0
        self.acceleration = 0

        self.vibrate_time = pygame.time.get_ticks()
        self.vibration_direction = 1 # This'll oscillate between 1 and -1. 1 = Moving downwards and -1 = Moving upwards
        self.vibration_dy = 0
        self.vibration_velocity = vibration_velocity

        self.image = None
        self.rect = None

    def draw(self):
        return

    def update(self):
        return

    # Shifts position of the particle to mimic vibration on y-axis w.r.t center of rect
    def vibrate(self, limit):
        if pygame.time.get_ticks() - self.vibrate_time > VIBRATION_COOLDOWN:
            dy = 0

            # If moving downwards
            if self.vibration_direction == 1:
                # Less than limit, we keep going downward
                if self.vibration_dy < limit:
                    dy += self.vibration_velocity
                # Reaching limit, set direction going upward
                else:
                    self.vibration_direction = -1
                    self.vibration_dy = limit

            if self.vibration_direction == -1:
                if self.vibration_dy > 0:
                    dy -= self.vibration_velocity
                else:
                    self.vibration_direction = 1
                    self.vibration_dy = 0

            self.vibration_dy += dy
            self.rect.y += dy


class Electron(Particle):
    def __init__(self):
        super().__init__(charge = -1, mass = 1, vibration_velocity = PLAYER_VIBRATION_VELOCITY) # assuming electron has unit mass

        # placeholder sprite for now
        self.image = pygame.image.load(os.path.join(PARTICLES_DIR, "electron.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(SCALE * self.image.get_width()), int(SCALE * self.image.get_height())))

        self.rect = self.image.get_rect()

    def draw(self, screen : pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        self.vibrate(VIBRATION_LIMIT)

class Positron(Particle):
    def __init__(self):
        super().__init__(charge = +1, mass = 1, vibration_velocity = ENEMY_VIBRATION_VELOCITY)

        # placeholder sprite for now
        self.image = pygame.image.load(os.path.join(PARTICLES_DIR, "positron.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(SCALE * self.image.get_width()), int(SCALE * self.image.get_height())))

        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        self.vibrate(VIBRATION_LIMIT)

class Player(Electron):
    def __init__(self, init_x, init_y):
        super().__init__()
        self.rect.x = init_x
        self.rect.y = init_y

class Enemy(Positron):
    def __init__(self, init_x, init_y):
        super().__init__()
        self.rect.x = init_x
        self.rect.y = init_y
