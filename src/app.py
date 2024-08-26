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


import json
import os
from pprint import pprint
import sys
from time import time
import re
import typer
from typer import Option
from enum import Enum
import atexit

# By default pygame prints its version to the console when imported. We deactivate that.
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import pygame.locals as pg
import pygame._sdl2 as sdl2


from src import pygame_utils
from src import time_utils
from src import constants
from src import platforms
from src.purpose import Purpose
from src.callback import CountdownCallback
from src.config import PucotiConfig


class Scene(Enum):
    MAIN = "main"
    HELP = "help"
    PURPOSE_HISTORY = "purpose_history"
    ENTERING_PURPOSE = "entering_purpose"

    def mk_layout(
        self, screen_size: tuple[float, float], has_purpose: bool, no_total: bool = False
    ) -> dict[str, pygame.Rect]:
        width, height = screen_size
        screen = pygame.Rect((0, 0), screen_size)

        if width > 200:
            screen = screen.inflate(-width // 10, 0)

        if self == Scene.HELP:
            layout = {"help": 1}
        elif self == Scene.PURPOSE_HISTORY:
            layout = {"purpose_history": 1}
        elif self == Scene.ENTERING_PURPOSE:
            if height < 60:
                layout = {"purpose": 1}
            elif height < 80:
                layout = {"purpose": 2, "time": 1}
            else:
                layout = {"purpose": 2, "time": 1, "totals": 0.5}
        elif self == Scene.MAIN:
            if height < 60:
                layout = {"time": 1}
            elif height < 80:
                layout = {"purpose": 1, "time": 2}
            else:
                layout = {"purpose": 1, "time": 2, "totals": 1}

            if not has_purpose:
                layout["time"] += layout.pop("purpose", 0)
        else:
            raise ValueError(f"Invalid scene: {self}")

        if no_total:
            layout.pop("totals", None)

        rects = {
            k: rect
            for k, rect in zip(layout.keys(), pygame_utils.split_rect(screen, *layout.values()))
        }

        # Bottom has horizontal layout with [total_time | purpose_time]
        if total_time_rect := rects.pop("totals", None):
            rects["total_time"], _, rects["purpose_time"] = pygame_utils.split_rect(
                total_time_rect, 1, 0.2, 1, horizontal=True
            )

        return rects


app = typer.Typer(add_completion=False)


def StyleOpt(help=None, **kwargs):
    return Option(help=help, rich_help_panel="Style", **kwargs)


@app.command(
    help="Stay on task with PUCOTI, a countdown timer built for simplicity and purpose.\n\nGUI Shortcuts:\n\n"
    + constants.SHORTCUTS.replace("\n", "\n\n")
)
@PucotiConfig.mk_typer_cli("initial_timer")
def main(config: PucotiConfig) -> None:
    pprint(config)

    history_file = config.history_file.expanduser()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.touch(exist_ok=True)

    pygame.init()
    pygame.mixer.init()
    pygame.key.set_repeat(300, 20)

    window = sdl2.Window(
        "PUCOTI", config.window.initial_size, borderless=True, always_on_top=True, resizable=True
    )
    window.get_surface().fill((0, 0, 0))
    window.flip()
    window_has_focus = True

    screen = window.get_surface()
    clock = pygame.time.Clock()

    position = 0
    platforms.place_window(window, *config.window.initial_position)
    platforms.set_window_to_sticky()

    initial_duration = time_utils.human_duration(config.initial_timer)
    start = round(time())
    timer_end = initial_duration
    last_rung = 0
    nb_rings = 0
    callbacks = [CountdownCallback(cfg) for cfg in config.run_at]

    purpose_history = [
        Purpose(**json.loads(line))
        for line in history_file.read_text().splitlines()
        if line.strip()
    ]
    purpose = ""
    purpose_start_time = int(time())
    history_lines = 10
    history_scroll = 0  # From the bottom
    show_relative_time = True
    hide_total = False

    last_scene = None
    scene = Scene.MAIN

    # Hook to save the last purpose end time when the program is closed.
    @atexit.register
    def save_last_purpose():
        if purpose:
            Purpose("").add_to_history(history_file)

    while True:
        last_scene = scene
        for event in pygame.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.WINDOWFOCUSGAINED:
                window_has_focus = True
            elif event.type == pg.WINDOWFOCUSLOST:
                window_has_focus = False
            elif event.type == pg.TEXTINPUT and scene == Scene.ENTERING_PURPOSE:
                purpose += event.text
            elif event.type == pg.KEYDOWN:
                if scene == Scene.HELP:
                    scene = Scene.MAIN
                elif scene == Scene.ENTERING_PURPOSE:
                    if event.key == pg.K_BACKSPACE:
                        if event.mod & pg.KMOD_CTRL:
                            purpose = re.sub(r"\S*\s*$", "", purpose)
                        else:
                            purpose = purpose[:-1]
                    elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_ESCAPE):
                        scene = Scene.MAIN

                elif scene == Scene.PURPOSE_HISTORY:
                    if event.key == pg.K_j:
                        history_scroll = max(0, history_scroll - 1)
                    elif event.key == pg.K_k:
                        history_scroll = min(
                            len([p for p in purpose_history if p.text]) - history_lines,
                            history_scroll + 1,
                        )
                    elif event.key == pg.K_l:
                        show_relative_time = not show_relative_time
                    else:
                        scene = Scene.MAIN
                elif event.key == pg.K_j:
                    timer_end -= 60 * 5 if pygame_utils.shift_is_pressed(event) else 60
                elif event.key == pg.K_k:
                    timer_end += 60 * 5 if pygame_utils.shift_is_pressed(event) else 60
                elif event.key in constants.NUMBER_KEYS:
                    new_duration = 60 * pygame_utils.get_number_from_key(event.key)
                    if pygame_utils.shift_is_pressed(event):
                        new_duration *= 10
                    timer_end = time_utils.compute_timer_end(new_duration, start)
                    initial_duration = new_duration
                elif event.key == pg.K_r:
                    timer_end = time_utils.compute_timer_end(initial_duration, start)
                elif event.key == pg.K_MINUS:
                    pygame_utils.scale_window(
                        window, 1 / constants.WINDOW_SCALE, constants.MIN_WINDOW_SIZE
                    )
                    platforms.place_window(window, *constants.POSITIONS[position])
                elif event.key == pg.K_PLUS or event.key == pg.K_EQUALS:
                    pygame_utils.scale_window(
                        window, constants.WINDOW_SCALE, constants.MIN_WINDOW_SIZE
                    )
                    platforms.place_window(window, *constants.POSITIONS[position])
                elif event.key == pg.K_p:
                    position = (position + 1) % len(constants.POSITIONS)
                    platforms.place_window(window, *constants.POSITIONS[position])
                elif event.key == pg.K_t:
                    hide_total = not hide_total
                elif event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                    scene = Scene.ENTERING_PURPOSE
                elif event.key in (pg.K_h, pg.K_QUESTION):
                    scene = Scene.HELP
                elif event.key == pg.K_l:
                    scene = Scene.PURPOSE_HISTORY

        if last_scene == Scene.ENTERING_PURPOSE and scene != last_scene:
            if not purpose_history or purpose != purpose_history[-1].text:
                purpose_start_time = round(time())
                purpose_history.append(Purpose(purpose))
                purpose_history[-1].add_to_history(history_file)

        layout = scene.mk_layout(window.size, bool(purpose), hide_total)

        screen.fill(config.color.background)

        # Render purpose, if there is space.
        if purpose_rect := layout.get("purpose"):
            t = config.font.normal.render(purpose, purpose_rect.size, config.color.purpose)
            r = screen.blit(t, t.get_rect(center=purpose_rect.center))
            if scene == Scene.ENTERING_PURPOSE and (time() % 1) < 0.7:
                if r.height == 0:
                    r.height = purpose_rect.height
                if r.right >= purpose_rect.right:
                    r.right = purpose_rect.right - 3
                pygame.draw.line(screen, config.color.purpose, r.topright, r.bottomright, 2)

        # Render time.
        remaining = timer_end - (time() - start)
        if time_rect := layout.get("time"):
            color = config.color.timer_up if remaining < 0 else config.color.timer
            t = config.font.big.render(
                time_utils.fmt_duration(abs(remaining)),
                time_rect.size,
                color,
                monospaced_time=True,
            )
            screen.blit(t, t.get_rect(center=time_rect.center))

        if total_time_rect := layout.get("total_time"):
            t = config.font.normal.render(
                time_utils.fmt_duration(time() - start),
                total_time_rect.size,
                config.color.total_time,
                monospaced_time=True,
            )
            screen.blit(t, t.get_rect(midleft=total_time_rect.midleft))

        if purpose_time_rect := layout.get("purpose_time"):
            t = config.font.normal.render(
                time_utils.fmt_duration(time() - purpose_start_time),
                purpose_time_rect.size,
                config.color.purpose,
                monospaced_time=True,
            )
            screen.blit(t, t.get_rect(midright=purpose_time_rect.midright))

        if help_rect := layout.get("help"):
            title = "PUCOTI Bindings"
            s = config.font.normal.table(
                [line.split(": ") for line in constants.SHORTCUTS.split("\n")],  # type: ignore
                help_rect.size,
                [config.color.purpose, config.color.timer],
                title=title,
                col_sep=": ",
                align=[pg.FONT_RIGHT, pg.FONT_LEFT],
                title_color=config.color.timer,
            )
            screen.blit(s, s.get_rect(center=help_rect.center))

        if purpose_history_rect := layout.get("purpose_history"):
            timestamps = [p.timestamp for p in purpose_history] + [time()]
            rows = [
                [
                    time_utils.fmt_duration(end_time - p.timestamp),
                    pygame_utils.shorten(p.text, 40),
                    time_utils.fmt_time(p.timestamp, relative=show_relative_time),
                ]
                for p, end_time in zip(purpose_history, timestamps[1:], strict=True)
                if p.text
            ]
            first_shown = len(rows) - history_lines - history_scroll
            last_shown = len(rows) - history_scroll
            hidden_rows = rows[:first_shown] + rows[last_shown:]
            rows = rows[first_shown:last_shown]

            headers = ["Span", "Purpose [J/K]", "Started [L]"]
            s = config.font.normal.table(
                [headers] + rows,
                purpose_history_rect.size,
                [config.color.total_time, config.color.purpose, config.color.timer],
                title="History",
                col_sep=": ",
                align=[pg.FONT_RIGHT, pg.FONT_LEFT, pg.FONT_RIGHT],
                title_color=config.color.purpose,
                hidden_rows=hidden_rows,
                header_line_color=config.color.purpose,
            )
            screen.blit(s, s.get_rect(center=purpose_history_rect.center))

        # Show border if focused
        if window_has_focus:
            pygame.draw.rect(screen, config.color.purpose, screen.get_rect(), 1)

        # If \ is pressed, show the rects in locals()
        if pygame.key.get_pressed()[pg.K_BACKSLASH]:
            debug_font = config.font.normal.get_font(20)
            for name, rect in locals().items():
                if isinstance(rect, pygame.Rect):
                    color = pygame_utils.random_color(name)
                    pygame.draw.rect(screen, color, rect, 1)
                    # and its name
                    t = debug_font.render(name, True, (255, 255, 255))
                    screen.blit(t, rect.topleft)

        # Ring the bell if the time is up.
        if (
            remaining < 0
            and time() - last_rung > config.ring_every
            and nb_rings != config.ring_count
        ):
            last_rung = time()
            nb_rings += 1
            pygame_utils.play(config.bell)
            if config.restart:
                timer_end = initial_duration + (round(time() + 0.5) - start)

        elif remaining > 0:
            nb_rings = 0
            last_rung = 0

        # And execute the callbacks.
        for callback in callbacks:
            callback.update(timer_end - (time() - start))

        window.flip()
        clock.tick(30)


if __name__ == "__main__":
    app()
