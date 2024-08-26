"""
This file contains code to handle platform specific code.
It covers functionnalities such as manipulating windows.
"""

import os
import platform
import subprocess
import sys
import warnings

import pygame


# Diego uses sway, and it needs a few tweaks as it's a non-standard window manager.
RUNS_ON_SWAY = os.environ.get("SWAYSOCK") is not None
IS_MACOS = sys.platform == "darwin" or platform.system() == "Darwin"

# Diego's version of pygame-ce fails to run directly on Wayland, so I force it to use X11.
if os.environ.get("SDL_VIDEODRIVER") == "wayland":
    os.environ["SDL_VIDEODRIVER"] = "x11"


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


def set_window_to_sticky():
    if IS_MACOS:
        try:
            from AppKit import (
                NSApplication,
                NSFloatingWindowLevel,
                NSWindowCollectionBehaviorCanJoinAllSpaces,
            )

            ns_app = NSApplication.sharedApplication()
            ns_window = ns_app.windows()[0]
            ns_window.setLevel_(NSFloatingWindowLevel)
            ns_window.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
        except Exception as e:
            print(e)
