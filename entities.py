import pygame
from config import *
import os

class Particle(pygame.sprite.Sprite):
    def __init__(self, charge, mass):
        super().__init__()
        self.charge = charge
        self.mass = mass

        self.position = 0
        self.angle = 0
        self.velocity = 0
        self.acceleration = 0


        self.image = None
        self.rect = None

    def draw(self):
        return

    def update(self):
        return


class Electron(Particle):
    def __init__(self):
        super().__init__(charge=-1, mass=1) # assuming electron has unit mass

        # placeholder sprite for now
        self.image = pygame.image.load(os.path.join(PARTICLES_DIR, "electron_sprite.png")).convert_alpha()
        self.rect = self.image.get_rect()

    def draw(self, screen : pygame.surface.Surface):
        screen.blit(self.image, self.rect)

    def update(self):
        return

class Positron(Particle):
    def __init__(self):
        super().__init__(charge=+1, mass=1)

class Player(Electron):
    def __init__(self, init_x, init_y):
        super().__init__()
        self.rect.x = init_x
        self.rect.y = init_y
