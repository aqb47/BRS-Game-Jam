import pygame
import math
import os
from enum import Enum

from config import *
from utils import *


# For applying powerup to player
class Powerup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


# Visual bar to represent the player's current health
class HealthBar(pygame.sprite.Sprite):
    def __init__(self, init_x, init_y):
        super().__init__()

        self.image = pygame.image.load(os.path.join(IMG_DIR, "health.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(HEALTH_SCALE * self.image.get_width()), int(HEALTH_SCALE * self.image.get_height())))

        self.rect = self.image.get_rect()
        self.rect.x = init_x
        self.rect.y = init_y

        # How many health icons we'll have
        self.count = 100 / ENEMY_DAMAGE

    def draw(self, screen):
        for x_pos in range(self.rect.x, int(self.rect.x + self.count * (self.image.get_width() + HEALTH_PADDING)), int(self.image.get_width() + HEALTH_PADDING)):
            screen.blit(self.image, (x_pos, self.rect.y))


# Essentially represents what the player is currently doing
class PlayerState(Enum):
    AIMING = 0
    MOVING = 1
    REVERSING = 2
    DEAD = 3


class Indicator(pygame.sprite.Sprite):
    def __init__(self, init_x, init_y, max_angular_amplitude):
        super().__init__()

        self.max_angular_amplitude = max_angular_amplitude
        self.cur_angular_amplitude = max_angular_amplitude

        # Indicator image
        self.original_image = pygame.image.load(os.path.join(IMG_DIR, "indicator.png")).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (int(INDICATOR_SCALE * self.original_image.get_width()), int(INDICATOR_SCALE * self.original_image.get_height())))
        self.original_image.set_alpha(INDICATOR_TRANSPARENCY)

        # Slice it and make it transparent before blitting to arrow
        self.image = get_circle_slice(self.original_image, -self.max_angular_amplitude, +self.max_angular_amplitude)

        self.is_visible = True

        self.rect = self.image.get_rect()
        self.rect.x = init_x
        self.rect.y = init_y

    # Update with player
    def update(self, player : Player):
        self.rect.center = player.rect.center

        # Change image if the maximum angular amplitude is changed by another class
        if self.cur_angular_amplitude != self.max_angular_amplitude:
            self.image = get_circle_slice(self.original_image, -self.max_angular_amplitude, +self.max_angular_amplitude)
            self.cur_angular_amplitude = self.max_angular_amplitude

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# For a pointer arrow indicating the angle for movement
class Arrow(pygame.sprite.Sprite):
    def __init__(self, init_x, init_y, reference_x, reference_y, angular_amplitude):
        super().__init__()

        # Arrow image
        self.image = pygame.image.load(os.path.join(IMG_DIR, "arrow.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(ARROW_SCALE * self.image.get_width()), int(ARROW_SCALE * self.image.get_height())))

        # We keep on rotating the image so we need a copy of the original
        self.original_image = self.image

        self.rect = self.image.get_rect()

        self.mouse_pos = pygame.math.Vector2(0, 0) # Position of mouse that will be continuously updated by Game()
        self.player_pos = pygame.math.Vector2(reference_x, reference_y) # Position of Player that will be mostly constant and changed upon its movement

        self.reference_distance = self.player_pos.distance_to((init_x, init_y)) 

        # Arrow angular amplitude is in radians
        self.angular_amplitude = math.radians(angular_amplitude) # Convert degree to radians
        self.angle = -self.angular_amplitude # In radians

        self.rect.x = init_x
        self.rect.y = init_y

        self.is_visible = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, player, camera_offset=(0, 0)):
        self.player_pos[0] = player.rect.centerx
        self.player_pos[1] = player.rect.centery

        # Convert the screen-space mouse position into world coordinates.
        mouse_world_pos = pygame.math.Vector2(self.mouse_pos) + camera_offset

        # Calculate angle between reference point (Player) and mouse position w.r.t horizontal
        dx = mouse_world_pos.x - self.player_pos.x
        dy = mouse_world_pos.y - self.player_pos.y

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


# Base class for electrons and positrons
class Particle(pygame.sprite.Sprite):
    def __init__(self, charge, mass, vibration_velocity):
        super().__init__()
        self.charge = charge
        self.mass = mass

        self.position = 0
        self.angle = 0
        self.target_angle = self.angle

        self.velocity = 0
        self.acceleration = 0
        self.friction = FRICTION
        self.attraction_displacement = pygame.math.Vector2()

        self.vibrate_time = pygame.time.get_ticks()
        self.vibration_direction = 1 # This'll oscillate between 1 and -1. 1 = Moving downwards and -1 = Moving upwards
        self.vibration_dy = 0
        self.vibration_velocity = vibration_velocity

        self.applied_friction = 0

        self.is_visible = True

        self.image = None
        self.rect = None
        self.hitbox_rect = None
        self.original_image = None

    def draw(self):
        return

    def update_hitbox(self):
        if self.hitbox_rect is None:
            self.hitbox_rect = self.rect.inflate(-self.rect.width // 2, -self.rect.height // 2)
        self.hitbox_rect.center = self.rect.center

    def update(self):
        self.vibrate(VIBRATION_LIMIT)

        # If a force is applied
        dx = 0
        dy = 0

        # Calculate new velocity and acceleration due to friction
        self.velocity += self.acceleration
        self.acceleration -= self.friction + self.applied_friction

        # If friction acts long enough and velocity is less than zero, we will cap it to zero
        if self.velocity <= 0:
            self.velocity = 0
            self.acceleration = 0
            self.applied_friction = 0

        dx += self.velocity * math.cos(-self.target_angle)
        dy += self.velocity * math.sin(-self.target_angle)

        self.rect.x += DISPLACEMENT_SCALE * dx
        self.rect.y += DISPLACEMENT_SCALE * dy

        self.update_hitbox()
        self.update_attraction()

    def apply_attraction(self, other):
        # Get distance between two particles
        offset = pygame.math.Vector2(other.rect.center) - self.rect.center
        distance = offset.length()

        # Check if distance is within limit
        if distance <= MINIMUM_ATTRACTION_DISTANCE or distance >= MAXIMUM_ATTRACTION_DISTANCE:
            return

        # Increment by unit vector * speed for attraction
        self.attraction_displacement += offset.normalize() * ATTRACTION_SPEED

    def update_attraction(self):
        self.rect.center += self.attraction_displacement

        self.attraction_displacement.x = 0
        self.attraction_displacement.y = 0

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

        self.original_image = self.image

        self.rect = self.image.get_rect()
        self.update_hitbox()

    def draw(self, screen : pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        super().update()


class Positron(Particle):
    def __init__(self):
        super().__init__(charge = +1, mass = 1, vibration_velocity = ENEMY_VIBRATION_VELOCITY)

        # placeholder sprite for now
        self.image = pygame.image.load(os.path.join(PARTICLES_DIR, "positron.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(SCALE * self.image.get_width()), int(SCALE * self.image.get_height())))

        self.original_image = self.image

        self.rect = self.image.get_rect()
        self.update_hitbox()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        super().update()


class Player(Electron):
    def __init__(self, init_x, init_y):
        super().__init__()
        self.rect.x = init_x
        self.rect.y = init_y
        self.state = PlayerState.AIMING # Initially start off by aiming

        self.health = 100

        self.last_pos = pygame.math.Vector2(self.rect.x, self.rect.y) # For reversing during a collision

    def update_state(self, new_state):
        if self.state != new_state:
            self.state = new_state

    # Changes acceleration and angle for electron
    def move(self, angle, initial_acceleration = INITIAL_ACCELERATION):
        self.update_state(PlayerState.MOVING)
        self.target_angle = angle

        if abs(self.last_pos.x - self.rect.x) >= 5 or abs(self.last_pos.y - self.rect.y) >= 5:
            self.last_pos.x = self.rect.x
            self.last_pos.y = self.rect.y

        # Apply acceleration at an angle
        self.acceleration = initial_acceleration
        
    def rotate_image(self, angle):
        x = self.rect.centerx
        y = self.rect.centery

        self.image = pygame.transform.rotate(self.original_image, -math.degrees(angle))
                
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def apply_friction(self):
        self.applied_friction += 0.75

    def update(self):
        super().update()
        if self.velocity == 0 and self.acceleration == 0:
            self.update_state(PlayerState.AIMING)
            self.applied_friction = 0

        # Wrap angle difference between +pi/-pi
        difference = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi

        if abs(difference) > MIN_ROTATION:
            rotation_angle = max(-ELECTRON_ROTATION, min(ELECTRON_ROTATION, difference))

            self.angle += rotation_angle
            self.rotate_image(self.angle)

        else:
            self.angle = self.target_angle


class Enemy(Positron):
    def __init__(self, init_x, init_y):
        super().__init__()
        self.rect.x = init_x
        self.rect.y = init_y
