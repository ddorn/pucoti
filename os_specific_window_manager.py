import sys
import os
import platform
import subprocess
import warnings

# Diegouses sway, and it needs a few tweaks as it's a non-standard window manager.
RUNS_ON_SWAY = os.environ.get("SWAYSOCK") is not None
IS_MACOS = sys.platform == 'darwin' or platform.system() == 'Darwin'

def set_window_to_float():
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
    elif RUNS_ON_SWAY:
         # Thanks gpt4! This moves the window while keeping it on the same display.
        cmd = (
            """swaymsg -t get_outputs | jq -r \'.[] | select(.focused) | .rect | "\\(.x + %d) \\(.y + %d)"\' | xargs -I {} swaymsg \'[title="PUCOTI"] floating enable, move absolute position {}\'"""
            % (x, y)
        )
        try:
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            warnings.warn(f"Failed to move window on sway: {e}")
