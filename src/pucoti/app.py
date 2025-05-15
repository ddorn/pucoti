#!/usr/bin/env python

"""
PUCOTI - A Purposeful Countdown Timer
Copyright (C) 2024  Diego Dorn

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
from pathlib import Path
from typing import Annotated
import typer
from click.core import ParameterSource


# By default pygame prints its version to the console when imported. We deactivate that.
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import pygame.locals as pg
import luckypot


from . import constants
from . import platforms
from . import pygame_utils
from .config import PucotiConfig, RunAtConfig, SocialConfig
from .screens.base_screen import PucotiScreen
from .screens.start_screen import StartScreen
from .context import Context
from .controller import Controller


class App(luckypot.App[PucotiScreen]):
    NAME = "PUCOTI"
    # INITIAL_STATE = StartScreen

    def __init__(self, config: PucotiConfig):
        self.config = config
        self.ctx = Context(
            config=config,
            app=self,
        )

        if config.window.start_small:
            self.INITIAL_SIZE = config.window.small_size
        else:
            self.INITIAL_SIZE = config.window.big_size

        assert config.window.small_size[0] <= config.window.big_size[0]
        assert config.window.small_size[1] <= config.window.big_size[1]

        self.WINDOW_KWARGS["borderless"] = config.window.borderless
        self.WINDOW_KWARGS["always_on_top"] = config.window.always_on_top
        self.WINDOW_KWARGS["resizable"] = config.window.resizable

        super().__init__()
        pygame.key.set_repeat(300, 20)

        if config.window.start_small:
            platforms.place_window(self.window, *config.window.initial_position)

        self.window_has_focus = True

        self.position_index = 0
        self.window_positions = list(constants.POSITIONS)
        if config.window.initial_position not in self.window_positions:
            self.window_positions.insert(0, config.window.initial_position)

        self.controller_server = Controller()
        self.controller_server.start()

    @property
    def INITIAL_STATE(self):
        return lambda: StartScreen(self.ctx)

    @property
    def current_window_position(self):
        return self.window_positions[self.position_index % len(self.window_positions)]

    def handle_event(self, event) -> bool:
        # We want the state to handle the event first.
        if super().handle_event(event):
            return True

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                self.position_index += 1
                platforms.place_window(
                    self.ctx.app.window,
                    *self.current_window_position,
                )
            elif event.key == pg.K_SPACE:
                self.toggle_big_window()
            elif event.key == pg.K_MINUS:
                pygame_utils.scale_window(
                    self.window, 1 / constants.WINDOW_SCALE, constants.MIN_WINDOW_SIZE
                )
                platforms.place_window(self.window, *self.current_window_position)
            elif event.key in (pg.K_PLUS, pg.K_EQUALS):
                pygame_utils.scale_window(
                    self.window, constants.WINDOW_SCALE, constants.MIN_WINDOW_SIZE
                )
                platforms.place_window(self.window, *self.current_window_position)
            else:
                return False
            return True

        elif event.type == pg.WINDOWFOCUSGAINED:
            self.window_has_focus = True
        elif event.type == pg.WINDOWFOCUSLOST:
            self.window_has_focus = False
        return False

    def draw(self):
        super().draw()

        # Show border if focused
        if self.window_has_focus:
            screen = self.gfx.surf
            pygame.draw.rect(screen, self.config.color.purpose, screen.get_rect(), 1)

    def on_state_enter(self, state):
        super().on_state_enter(state)
        state.ctx = self.ctx

    def on_exit(self):
        self.controller_server.stop()
        return super().on_exit()

    def toggle_big_window(self):
        """Make the window big if small and vice-versa."""
        w_width, w_height = self.window.size
        small_width, small_height = self.config.window.small_size

        if w_width <= small_width or w_height <= small_height:
            self.make_window_big()
        else:
            self.make_window_small()

    def make_window_small(self):
        """Make the window small."""
        self.window.size = self.config.window.small_size
        platforms.place_window(
            self.window,
            *self.current_window_position,
        )

    def make_window_big(self):
        """Make the window big."""
        self.window.size = self.config.window.big_size


defaults = PucotiConfig()

if constants.CONFIG_PATH.exists():
    defaults = defaults.merge_partial_from_file(constants.CONFIG_PATH)


def print_config(value: bool):
    if value:
        print(PucotiConfig.generate_default_config_yaml())
        raise typer.Exit()


def doc(name: str, argument: bool = False, **kwargs):
    if argument:
        cls = typer.Argument
    else:
        cls = typer.Option

    if help_ := PucotiConfig.doc_for(name):
        kwargs["help"] = help_ + kwargs.get("help", "")

    return cls(**kwargs)


app = typer.Typer(add_completion=False)


@app.command(
    help="Stay on task with PUCOTI, a countdown timer built for simplicity and purpose.\n\nGUI Shortcuts:\n\n"
    + constants.SHORTCUTS.replace("\n", "\n\n")
)
def run(
    # fmt: off
    ctx: typer.Context,
    initial_timer: Annotated[str, doc("initial_timer", argument=True)] = defaults.initial_timer,
    restart: Annotated[bool, doc("restart")] = defaults.restart,
    run_at: Annotated[list[RunAtConfig], doc("run_at", help=" E.g. '-1m:suspend'", parser=RunAtConfig.from_string)] = [],
    borderless: Annotated[bool, doc("window.borderless")] = defaults.window.borderless,
    social: Annotated[SocialConfig, typer.Option(help="Share timer online. Fmt: 'usernam@room'", parser=SocialConfig.from_string)] = None,
    print_config: Annotated[bool, typer.Option("--print-config", help="Print the configuration and exit", callback=print_config, is_eager=True)] = False,
    config_file: Annotated[Path, typer.Option("--config", help="Path to the configuration file")] = constants.CONFIG_PATH,
    # fmt: on
) -> None:
    config = PucotiConfig()
    if config_file.exists():
        config = config.merge_partial_from_file(config_file)
    else:
        raise typer.BadParameter(f"File {config_file} does not exist.")

    to_ignore = {"config_file", "print_config"}
    renamed = {
        "borderless": "window.borderless",
    }
    for param, source in ctx._parameter_source.items():
        if source == ParameterSource.COMMANDLINE:
            if param in to_ignore:
                continue

            param = renamed.get(param, param)

            # Build a dict like {window: {borderless: True}}
            data = ctx.params[param]
            for part in reversed(param.split(".")):
                data = {part: data}

            config = config.merge_partial(data)

    App(config).run()


if __name__ == "__main__":
    app()
