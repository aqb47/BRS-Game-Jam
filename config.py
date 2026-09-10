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

# Font

FONT_DIR = BASE_DIR / "fonts"
SCORE_FONT = FONT_DIR / "PixelifySans-Regular.ttf"
SCORE_FONT_SIZE = 50
SCORE_POS = (700, 10)
SCORE_COLOR = (255, 255, 255)


# Player

PLAYER_START_X = 10
PLAYER_START_Y = SCREEN_HEIGHT // 2

INITIAL_ACCELERATION = 12
FRICTION = 2

# Particles

VIBRATION_COOLDOWN = 50
PLAYER_VIBRATION_VELOCITY = 2
ENEMY_VIBRATION_VELOCITY = 1
VIBRATION_LIMIT = 20

# Arrow
ARROW_SCALE = 2
