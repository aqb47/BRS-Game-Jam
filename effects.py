import random
import pygame

from config import *


class CRTEffects:
    def __init__(self, screen):
        self.screen = screen

        self.pixelation_surface = pygame.Surface((SCREEN_WIDTH // PIXELATION_SCALE, SCREEN_HEIGHT // PIXELATION_SCALE))

        self.glow_surface = pygame.Surface((SCREEN_WIDTH // GLOW_SCALE, SCREEN_HEIGHT // GLOW_SCALE))

        self.glitch_surface = pygame.Surface((GLITCH_EFFECT_WIDTH, MAX_SLICE))

        self.scanline_overlay = self.create_scanline_overlay()

        self.static_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    # Apply all effects
    def apply(self):
        self.apply_scanlines()
        self.apply_pixelation()
        # self.apply_glow()
        self.apply_rolling_static()
        self.apply_flicker()
        self.apply_glitch_effect()

    def apply_scanlines(self):
        self.screen.blit(self.scanline_overlay, (0, 0))

    def apply_pixelation(self):
        pygame.transform.scale(self.screen, self.pixelation_surface.get_size(), self.pixelation_surface)

        pygame.transform.scale(self.pixelation_surface, self.screen.get_size(), self.screen)

    def apply_flicker(self):
        if random.randint(0, 20) == 0:
            self.screen.fill((5, 5, 5), special_flags=pygame.BLEND_RGB_ADD)

    def apply_glow(self):
        pygame.transform.smoothscale(self.screen, self.glow_surface.get_size(), self.glow_surface)

        pygame.transform.smoothscale(self.glow_surface, self.screen.get_size(), self.screen)

    def apply_glitch_effect(self):
        if random.random() >= 0.01:
            return

        y_pos = random.randint(0, SCREEN_HEIGHT - MAX_SLICE)
        slice_height = random.randint(MIN_SLICE, MAX_SLICE)
        offset = random.randint(-GLITCH_EFFECT_OFFSET, GLITCH_EFFECT_OFFSET)
        slice_area = pygame.Rect(0, y_pos, GLITCH_EFFECT_WIDTH, slice_height)

        self.glitch_surface.blit(self.screen, (0, 0), slice_area)
        self.screen.blit(self.glitch_surface, (offset, y_pos), pygame.Rect(0, 0, GLITCH_EFFECT_WIDTH, slice_height))

    def apply_rolling_static(self):
        has_static = False
        for y_pos in range(0, SCREEN_HEIGHT, STATIC_STEP):
            if random.random() >= STATIC_CHANCE:
                continue

            if not has_static:
                self.static_surface.fill((0, 0, 0, 0))
                has_static = True
            pygame.draw.line(self.static_surface, (255, 255, 255, random.randint(20, 70)), (0, y_pos), (SCREEN_WIDTH, y_pos))

        if has_static:
            self.screen.blit(self.static_surface, (0, 0))

    def create_scanline_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y_pos in range(0, SCREEN_HEIGHT, SCANLINE_STEP):
            pygame.draw.line(overlay, (0, 0, 0, 40), (0, y_pos), (SCREEN_WIDTH, y_pos))
        return overlay
