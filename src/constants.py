import os
import uuid

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame.locals as pg
from pathlib import Path


USER_ID = str(uuid.uuid4())
CONFIG_FILE = Path("~/.config/pucoti/default.yaml").expanduser()
ASSETS = Path(__file__).parent.parent / "assets"
BELL = ASSETS / "bell.mp3"
BIG_FONT = ASSETS / "Bevan-Regular.ttf"
FONT = BIG_FONT
WINDOW_SCALE = 1.2
MIN_WINDOW_SIZE = 15, 5
POSITIONS = [(-5, -5), (5, 5), (5, -5), (-5, 5)]
SHORTCUTS = """
j k: -/+ 1 minute
J K: -/+ 5 minutes
0-9: set duration
shift 0-9: set duration *10min
R: reset timer
RETURN: enter purpose
L: list purpose history
T: toggle total time
P: reposition window
- +: (in/de)crease window size
H ?: show this help
""".strip()
HELP = f"""
PUCOTI

{SHORTCUTS}
""".strip()

NUMBER_KEYS = [pg.K_0, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9]
UPDATE_SERVER_EVERY = 30  # seconds
