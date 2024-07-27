"""
This file contains code to handle platform specific code.
It covers functionnalities such as manipulating windows.
"""

import subprocess
import warnings

import pygame

from .utils import clamp
from .constants import MIN_HEIGHT, MIN_WIDTH, RUNS_ON_SWAY


def adjust_window_size(window, scale_factor: float):
    display_info = pygame.display.Info()
    max_width = display_info.current_w
    max_height = display_info.current_h

    new_width = window.size[0] * scale_factor
    new_height = window.size[1] * scale_factor

    clamped_new_width = clamp(new_width, MIN_WIDTH, max_width)
    clamped_new_height = clamp(new_height, MIN_HEIGHT, max_height)

    window.size = clamped_new_width, clamped_new_height


def place_window(window, x: int, y: int):
    """Place the window at the desired position."""

    info = pygame.display.Info()
    size = info.current_w, info.current_h

    if x < 0:
        x = size[0] + x - window.size[0]
    if y < 0:
        y = size[1] + y - window.size[1]

    # Is there a way to know if this worked? It doesn't on sway.
    # It works on some platforms.
    window.position = (x, y)

    if RUNS_ON_SWAY:
        # Thanks gpt4! This moves the window while keeping it on the same display.
        cmd = (
            """swaymsg -t get_outputs | jq -r \'.[] | select(.focused) | .rect | "\\(.x + %d) \\(.y + %d)"\' | xargs -I {} swaymsg \'[title="PUCOTI"] floating enable, move absolute position {}\'"""
            % (x, y)
        )
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            warnings.warn(f"Failed to move window on sway: {e}")
