"""
This file countains a lot of small, independent utility functions, mostly to
convert times, format strings, process pygame events and perform other small
conversions.
"""

from random import random
from time import time
from datetime import datetime
import pygame


def fmt_duration(seconds):
    if seconds < 0:
        return "-" + fmt_duration(-seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    else:
        return "%02d:%02d" % (minutes, seconds)


def fmt_time_relative(seconds):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc

    Adapted from https://stackoverflow.com/a/1551394/6160055
    """

    now = datetime.now()
    if isinstance(seconds, (int, float)):
        seconds = datetime.fromtimestamp(seconds)

    diff = now - seconds
    second_diff = diff.seconds
    day_diff = diff.days

    assert day_diff >= 0

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + "s ago"
        if second_diff < 120:
            return f"1m {second_diff % 60}s ago"
        if second_diff < 3600:
            return str(second_diff // 60) + "m ago"
        if second_diff < 7200:
            return f"1h {second_diff % 3600 // 60}m ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + "h ago"
    if day_diff <= 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"


def fmt_time_absoulte(seconds):
    now = datetime.now()
    if isinstance(seconds, (int, float)):
        seconds = datetime.fromtimestamp(seconds)

    diff = now - seconds
    day_diff = diff.days

    assert day_diff >= 0

    if day_diff == 0:
        return f"at {seconds.strftime('%H:%M')}"
    if day_diff == 1:
        return f"Yest at {seconds.strftime('%H:%M')}"
    if day_diff < 7:  # e.g. Tue at 12:34
        return f"{seconds.strftime('%a')} at {seconds.strftime('%H:%M')}"
    # Same month: Tue 12 at 12:34
    if day_diff < 31 and now.month == seconds.month:
        return f"{seconds.strftime('%a %d')} at {seconds.strftime('%H:%M')}"
    # Same year: Tue 12 Jan at 12:34
    if now.year == seconds.year:
        return f"{seconds.strftime('%a %d %b')} at {seconds.strftime('%H:%M')}"
    # Full date: Tue 12 Jan 2023 at 12:34
    return f"{seconds.strftime('%a %d %b %Y')} at {seconds.strftime('%H:%M')}"


def fmt_time(seconds, relative=True):
    return fmt_time_relative(seconds) if relative else fmt_time_absoulte(seconds)


def compute_timer_end(timer, start):
    # +0.5 to show visually round time -> more satisfying
    return timer + (round(time() + 0.5) - start)


def shorten(text: str, max_len: int) -> str:
    """Shorten a text to max_len characters, adding ... if necessary."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."  # 3 for the ...


def color_from_name(name: str) -> tuple[int, int, int]:
    instance = random.Random(name)
    return instance.randint(0, 255), instance.randint(0, 255), instance.randint(0, 255)


def clamp(value, mini, maxi):
    if value < mini:
        return mini
    if value > maxi:
        return maxi
    return value


def human_duration(duration: str) -> int:
    """Convert a human duration such as "1h 30m" to seconds."""

    if duration.startswith("-"):
        return -human_duration(duration[1:])

    # Parse the duration.
    total = 0
    multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    for part in duration.split():
        try:
            total += int(part[:-1]) * multiplier[part[-1]]
        except (ValueError, KeyError):
            raise ValueError(f"Invalid duration part: {part}")

    return total


def shift_is_pressed(event):
    return event.mod & pygame.KMOD_SHIFT


def get_number_from_key(key):
    return int(pygame.key.name(key))
