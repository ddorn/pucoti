import sys
import platform
import subprocess

def is_macos():
    return sys.platform == 'darwin' or platform.system() == 'Darwin'

def set_window_to_float():
    if is_macos():
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
    else:
        try:
            cmd = f'swaymsg "[title=\\"PUCOTI\\"] floating enable, move absolute position {x} {y}"'
            # Thanks gpt4!
            cmd = (
                """swaymsg -t get_outputs | jq -r \'.[] | select(.focused) | .rect | "\\(.x + %d) \\(.y + %d)"\' | xargs -I {} swaymsg \'[title="PUCOTI"] floating enable, move absolute position {}\'"""
                % (x, y)
            )
            print("Running:", cmd)
            subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
