from . import db
from . import platforms
import time


def get_activity(duration: float = 1) -> db.FocusedWindow:
    title, klass = platforms.get_active_window_title_and_class()
    now = time.time()
    return db.FocusedWindow(
        start=now,
        end=now + duration,
        window_title=title,
        window_class=klass,
    )


def log_activity(duration: float = 1):
    db.store(get_activity(duration=duration))
