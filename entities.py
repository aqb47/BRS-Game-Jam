import pygame

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

class Positron(Particle):
    def __init__(self):
        super().__init__(charge=+1, mass=1)

class Player(Electron):
    def __init__(self):
        super().__init__()
