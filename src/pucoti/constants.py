import os
import uuid

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame.locals as pg
from pathlib import Path
import platformdirs


def load_or_create_user_id(path: Path) -> str:
    if path.exists():
        return path.read_text().strip()

    path.parent.mkdir(parents=True, exist_ok=True)
    user_id = str(uuid.uuid4())
    path.write_text(user_id)
    return user_id


DIRS = platformdirs.PlatformDirs("pucoti", "ddorn", ensure_exists=True)
CONFIG_PATH = Path(DIRS.user_config_dir) / "default.yaml"
DATA_DIR = Path(DIRS.user_data_dir)
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(DIRS.user_data_dir) / "pucoti.db"

CLIENT_ID_PATH = DATA_DIR / "client_id"
USER_ID = load_or_create_user_id(CLIENT_ID_PATH)

UMAMI_URL_BASE = "https://umami.therandom.space"
UMAMI_WEBSITE_ID = "465a03b6-3e60-42c3-ad68-3f36b958c4e2"
UMAMI_HOSTNAME = "pucoti-app"

print(f"Configuration file: {CONFIG_PATH}")

CONTROLER_PORT = 8421

ASSETS = Path(__file__).parent / "assets"
BELL = ASSETS / "bell.mp3"
ICONS_FOLDER = ASSETS / "icons"
BIG_FONT = ASSETS / "Bevan-Regular.ttf"
FONT = BIG_FONT
PUCOTI_ICON = ICONS_FOLDER / "pucoti_icon.png"

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
SPACE: toggle big window
P: reposition window
- +: (in/de)crease window size
H ?: show this help
""".strip()
HELP = f"""
PUCOTI

{SHORTCUTS}
""".strip()

NUMBER_KEYS = [pg.K_0, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9]
UPDATE_SERVER_EVERY = 5  # seconds
