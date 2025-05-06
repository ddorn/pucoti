from functools import cached_property
from pathlib import Path
from dataclasses import field
from typing import Annotated, Literal, Self

from pydantic import Field


from . import constants
from .dfont import DFont
from .base_config import Config


class RunAtConfig(Config):
    """
    Run commands at specific times, possibly repeatedly.

    Times for `at` and `every` are human-readable durations, like '1h 30m 15s'.
    If `cmd_type` is `shell`, the default, the command is run directly in the system shell.
    If `cmd_type` is `python`, the command is run in the same Python process as PUCOTI, and can import modules.
        In particular, it has a access to `app`
    """

    at: str = "-1m"
    cmd: str = "notify-send 'Time is up by one minute!'"
    every: str | None = None
    cmd_type: Annotated[
        Literal["shell", "python"], Field(description="Can be 'shell' or 'python'")
    ] = "shell"

    @classmethod
    def from_string(cls, string: str) -> Self:
        at, cmd = string.split(":", 1)
        return cls(at=at, cmd=cmd)


class FontConfig(Config):
    timer: Annotated[Path, Field(description="Font file for the big timer")] = constants.BIG_FONT
    rest: Annotated[Path, Field(description="Font for everything else")] = constants.FONT

    @cached_property
    def big(self):
        return DFont(self.timer)

    @cached_property
    def normal(self):
        return DFont(self.rest)


Color = tuple[int, int, int]


class ColorConfig(Config):
    """Colors can be both triplets of numbers or hexadecimal values"""

    timer: Color = (255, 224, 145)
    timer_up: Color = (255, 0, 0)
    purpose: Color = (183, 255, 183)
    total_time: Color = (183, 183, 255)
    background: Color = (0, 0, 0)


class WindowConfig(Config):
    initial_position: tuple[int, int] = (-5, -5)
    small_size: tuple[int, int] = (220, 80)
    big_size: tuple[int, int] = (800, 360)
    borderless: bool = True
    start_small: bool = False
    resizable: bool = True
    always_on_top: bool = True


class SocialConfig(Config):
    """To share your timer with others"""

    enabled: bool = False
    room: str = "public"
    username: str = ""
    send_purpose: bool = True
    server: str = "https://pucoti.therandom.space"

    @classmethod
    def from_string(cls, string: str) -> Self:
        username, room = string.split("@", 1)
        return cls(username=username, room=room, enabled=True)


class PucotiConfig(Config):
    """
    The main configuration for PUCOTI.

    This file should be placed at ~/.config/pucoti/config.yaml.
    """

    # You can have multiple presets, by separating the yaml documents with "---".

    # preset: str = "default"
    initial_timer: Annotated[
        str, Field(description="The initial timer duration (e.g. '2m 30s')")
    ] = "5m"
    bell: Annotated[Path, Field(description="Path to the file played when time is up")] = (
        constants.BELL
    )
    ring_count: Annotated[
        int,
        Field(
            description="Number of times the bells plays when the time is up. -1 means no limit."
        ),
    ] = -1
    ring_every: Annotated[int, Field(description="Time between bells, in seconds")] = 20
    restart: Annotated[bool, Field(description="Restart the timer when it reaches 0")] = False
    history_file: Annotated[Path, Field(description="Path to save the history of purposes")] = Path(
        "~/.pucoti_history"
    )
    font: FontConfig = FontConfig()
    color: ColorConfig = ColorConfig()
    window: WindowConfig = WindowConfig()
    run_at: list[RunAtConfig] = field(default_factory=list)
    social: SocialConfig = SocialConfig()
