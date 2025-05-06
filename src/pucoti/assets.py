from functools import lru_cache

import pygame

from .constants import ICONS_FOLDER


@lru_cache()
def load_icon(name: str, color):
    # The icon is grayscale, and we want to convert it to:
    # white = transparent
    # black = color
    # and in between, interpolate the color to transparent.
    # So we need to:
    # 1. Load the icon
    # 2. invert the color
    # 3. create a new surface with the same size as the icon, and filled with color
    # 4. multiply the icon with the new surface
    icon = pygame.image.load(ICONS_FOLDER / f"{name}.png").convert_alpha()
    icon = pygame.transform.invert(icon)
    surf = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
    surf.fill(color)
    icon = icon.convert_alpha()
    surf.blit(icon, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return surf
