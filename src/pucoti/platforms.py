"""
This file contains code to handle platform specific code.
It covers functionnalities such as manipulating windows.
"""

import os
import platform
import subprocess
import sys
import warnings
import traceback

import pygame


# Diego uses sway, and it needs a few tweaks as it's a non-standard window manager.
RUNS_ON_SWAY = os.environ.get("SWAYSOCK") is not None
IS_MACOS = sys.platform == "darwin" or platform.system() == "Darwin"
RUNS_ON_XORG = os.environ.get("XDG_SESSION_TYPE") == "x11"


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


def get_active_window_title_and_class(return_empty_string_on_error: bool = True) -> tuple[str, str]:
    """Get the title and class of the active window."""

    try:
        wm_name, wm_class = _get_active_window_title_and_class()
    except NotImplementedError:
        # We raised this one explicitly, and it should always be propagated.
        raise
    except Exception:
        if return_empty_string_on_error:
            traceback.print_exc()
            wm_name = wm_class = ""
        else:
            raise

    return wm_name, wm_class


def _get_active_window_title_and_class() -> tuple[str, str]:
    if RUNS_ON_SWAY:
        a = subprocess.check_output(
            "swaymsg -t get_tree | jq -r '.. | select(.type?) | select(.focused) | .name, .app_id'",
            shell=True,
            text=True,
        ).splitlines()

        wm_name = a[0]
        wm_class = a[1]

    elif RUNS_ON_XORG:
        a = subprocess.check_output(
            "xprop -id $(xdotool getwindowfocus) -notype WM_NAME WM_CLASS",
            shell=True,
            text=True,
        ).splitlines()

        wm_name = a[0].partition(" = ")[2][1:-1]
        wm_class = a[1].partition(" = ")[2]

    elif IS_MACOS:
        # GPT-4 code. Not tested.
        from AppKit import NSWorkspace

        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        wm_name = active_app.localizedName()
        wm_class = active_app.bundleIdentifier()

    else:
        raise NotImplementedError("This window manager is not supported.")

    return wm_name, wm_class
