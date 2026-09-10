# Game variables, config stuff, data for adjusting things will go here
from pathlib import Path

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(0.8 * SCREEN_WIDTH)

FPS = 60

BG = (2, 24, 43) # DARK BLUE (02182B)

SCALE = 3

# Paths

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "img"

PARTICLES_DIR = IMG_DIR / "particles"

# Player

PLAYER_START_X = 10
PLAYER_START_Y = SCREEN_HEIGHT // 2

# Particles

VIBRATION_COOLDOWN = 100
PLAYER_VIBRATION_VELOCITY = 2
ENEMY_VIBRATION_VELOCITY = 1
VIBRATION_LIMIT = 20
