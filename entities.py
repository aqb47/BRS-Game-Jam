import pygame
import math
import os
from enum import Enum

from config import *


class PlayerState(Enum):
    AIMING = 0
    MOVING = 1


# For a pointer arrow indicating the angle for movement
class Arrow(pygame.sprite.Sprite):
    def __init__(self, init_x, init_y, reference_x, reference_y, angular_amplitude):
        self.image = pygame.image.load(os.path.join(IMG_DIR, "arrow.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(ARROW_SCALE * self.image.get_width()), int(ARROW_SCALE * self.image.get_height())))
        self.original_image = self.image

        self.rect = self.image.get_rect()

        self.mouse_pos = pygame.math.Vector2(0, 0) # Position of mouse that will be continuously updated by Game()
        self.player_pos = pygame.math.Vector2(reference_x, reference_y) # Position of Player that will be mostly constant and changed upon its movement

        self.reference_distance = self.player_pos.distance_to((init_x, init_y)) 

        self.angular_amplitude = math.radians(angular_amplitude) # Convert degree to radians
        self.angle = -self.angular_amplitude # In radians

        self.rect.x = init_x
        self.rect.y = init_y

        self.is_visible = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, player):
        self.player_pos[0] = player.rect.centerx
        self.player_pos[1] = player.rect.centery

        # Calculate angle between reference point (Player) and mouse position w.r.t horizontal
        dx = self.mouse_pos[0] - self.player_pos[0]
        dy = self.mouse_pos[1] - self.player_pos[1]

        # Get angles in radians and limit it
        angle = math.atan2(dy, dx)
        if angle > self.angular_amplitude: angle = self.angular_amplitude
        elif angle < -self.angular_amplitude: angle = -self.angular_amplitude

        new_x = self.reference_distance * math.cos(angle) + self.player_pos.x # rcos(theta) + x0
        new_y = self.reference_distance * math.sin(angle) + self.player_pos.y # rsin(theta) + y0

        # Rotate image
        self.image = pygame.transform.rotate(self.original_image, -math.degrees(angle))
        self.rect = self.image.get_rect()

        self.rect.center = (new_x, new_y)
        self.angle = -angle


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
    # TODO: Use a sine function here, it'd look better 
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

            self.vibrate_time = pygame.time.get_ticks()


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

        # If a force is applied
        dx = 0
        dy = 0

        # Calculate new velocity and acceleration due to friction
        self.velocity += self.acceleration
        self.acceleration -= FRICTION

        # If friction acts long enough and velocity is less than zero, we will cap it to zero
        if self.velocity <= 0:
            self.velocity = 0
            self.acceleration = 0
            self.angle = 0

        dx += self.velocity * math.cos(-self.angle)
        dy += self.velocity * math.sin(-self.angle)

        self.rect.x += dx
        self.rect.y += dy


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
        self.state = PlayerState.AIMING # Initially start off by aiming

        self.angle = 0

    def update_state(self, new_state):
        if self.state != new_state:
            self.state = new_state

    # Changes acceleration and angle for electron
    def move(self, angle):
        self.update_state(PlayerState.MOVING)

        # Apply acceleration at an angle
        self.acceleration = INITIAL_ACCELERATION
        self.angle = angle

    def update(self):
        super().update()
        if self.velocity == 0 and self.acceleration == 0:
            self.update_state(PlayerState.AIMING)

class Enemy(Positron):
    def __init__(self, init_x, init_y):
        super().__init__()
        self.rect.x = init_x
        self.rect.y = init_y
