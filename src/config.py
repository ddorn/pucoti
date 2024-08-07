from functools import cached_property
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Annotated

import typer

from src import constants
from src.dfont import DFont
from src.base_config import Config, SingleArgConfig


@dataclass(frozen=True)
class RunAtConfig(SingleArgConfig):
    """Run commands at specific times."""

    at: str = "-1m"
    cmd: str = "notify-send 'Time is up by one minute!'"
    # every: str | None = None


@dataclass(frozen=True)
class FontConfig(Config):
    timer: Annotated[Path, "Font file for the big timer"] = constants.BIG_FONT
    rest: Annotated[Path, "Font for everything else"] = constants.FONT

    @cached_property
    def big(self):
        return DFont(self.timer)

    @cached_property
    def normal(self):
        return DFont(self.rest)


Color = tuple[int, int, int]


@dataclass(frozen=True)
class ColorConfig(Config):
    """Colors can be both triplets of numbers or hexadecimal values"""

    timer: Color = (255, 224, 145)
    timer_up: Color = (255, 0, 0)
    purpose: Color = (183, 255, 183)
    total_time: Color = (183, 183, 255)
    background: Color = (0, 0, 0)


@dataclass(frozen=True)
class WindowConfig(Config):
    initial_position: tuple[int, int] = (-5, -5)
    initial_size: tuple[int, int] = (220, 80)
    borderless: bool = True


@dataclass(frozen=True)
class PucotiConfig(Config):
    """
    The main configuration for PUCOTI.

    This file should be placed at ~/.config/pucoti/config.yaml.
    You can have multiple presets, by separating the yaml documents with "---".
    """

    # preset: str = "default"
    initial_timer: Annotated[str, "The initial timer duration"] = "5m"
    bell: Annotated[Path, "Path to the file played when time is up"] = constants.BELL
    ring_every: Annotated[int, "Time between bells, in seconds"] = 20
    ring_count: Annotated[int, "Number of bells played when the time is up. -1 means no limit."] = (
        -1
    )
    restart: Annotated[bool, "Restart the timer when it reaches 0"] = False
    history_file: Annotated[Path, "Path to save the history of purposes"] = Path(
        "~/.pucoti_history"
    )
    font: FontConfig = FontConfig()
    color: ColorConfig = ColorConfig()
    window: WindowConfig = WindowConfig()
    run_at: list[RunAtConfig] = field(default_factory=list)


if __name__ == "__main__":
    conf_content = PucotiConfig.generate_default_config_yaml()
    # print(conf_content)

    data = PucotiConfig.load(conf_content)
    # print(data)
    # print(PucotiConfig())

    assert asdict(data) == asdict(PucotiConfig())

    @PucotiConfig.mk_typer_cli("initial_timer")
    def main(config):
        print(config)
        from pprint import pprint

        pprint(asdict(config))

    app = typer.Typer(add_completion=False)
    app.command()(main)

    app()
