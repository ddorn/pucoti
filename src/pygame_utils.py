"""
This module provides utility functions for working with Pygame.
"""

import random
import pygame


def shorten(text: str, max_len: int) -> str:
    """Shorten a text to max_len characters, adding ... if necessary."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."  # 3 for the ...


def random_color(seed: str) -> tuple[int, int, int]:
    instance = random.Random(seed)
    return instance.randint(0, 255), instance.randint(0, 255), instance.randint(0, 255)


def shift_is_pressed(event):
    return event.mod & pygame.KMOD_SHIFT


def get_number_from_key(key):
    return int(pygame.key.name(key))


def play(sound):
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()


def split_rect(rect, *ratios, horizontal: bool = False, spacing: float = 0):
    """Split a rect vertically in ratios."""
    total_ratio = sum(ratios) + spacing
    ratios = [r / total_ratio for r in ratios]
    if len(ratios) == 1:
        absolute_spacing = 0
    else:
        absolute_spacing = int(spacing * rect.height) / (len(ratios) - 1)
    cummulative_ratios = [0] + [sum(ratios[:i]) for i in range(1, len(ratios) + 1)]
    if horizontal:
        xs = [rect.left + int(rect.width * r) for r in cummulative_ratios]
        rects = [
            pygame.Rect(xs[i], rect.top, xs[i + 1] - xs[i], rect.height) for i in range(len(ratios))
        ]
        # Add the spacing
        for i in range(1, len(rects)):
            rects[i].left += absolute_spacing * i
    else:
        ys = [rect.top + int(rect.height * r) for r in cummulative_ratios]
        rects = [
            pygame.Rect(rect.left, ys[i], rect.width, ys[i + 1] - ys[i]) for i in range(len(ratios))
        ]
        # Add the spacing
        for i in range(1, len(rects)):
            rects[i].top += absolute_spacing * i
    return rects


def clamp(value, mini, maxi):
    if value < mini:
        return mini
    if value > maxi:
        return maxi
    return value


def scale_window(window, scale_factor: float, min_size: tuple[int, int]):
    display_info = pygame.display.Info()
    max_width = display_info.current_w
    max_height = display_info.current_h

    new_width = window.size[0] * scale_factor
    new_height = window.size[1] * scale_factor

    clamped_new_width = clamp(new_width, min_size[0], max_width)
    clamped_new_height = clamp(new_height, min_size[1], max_height)

    window.size = clamped_new_width, clamped_new_height
