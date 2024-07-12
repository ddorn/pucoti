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


from datetime import datetime
from dataclasses import dataclass
import dataclasses
from functools import lru_cache
import json
import os
import subprocess
import sys
from time import time
from typing import Annotated
from pathlib import Path
import re
import typer
from typer import Argument, Option
from enum import Enum
import random
import atexit
from os_specific_window_manager import set_window_to_float


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
if os.environ.get("SDL_VIDEODRIVER") == "wayland":
    os.environ["SDL_VIDEODRIVER"] = "x11"

import pygame
import pygame.locals as pg
import pygame._sdl2 as sdl2


ASSETS = Path(__file__).parent / "assets"
BELL = ASSETS / "bell.mp3"
BIG_FONT = ASSETS / "Bevan-Regular.ttf"
FONT = BIG_FONT
WINDOW_SCALE = 1.2
POSITIONS = [(-5, -5), (5, 5), (5, -5), (-5, 5)]
SHORTCUTS = """
J K: -/+ 1 minute
R: reset timer
RETURN: enter purpose
L: list purpose history
T: toggle total time
P: reposition window
- +: (in/de)crease window size
H ?: show this help
""".strip()
HELP = f"""
PUCOTI

{SHORTCUTS}
""".strip()


def fmt_duration(seconds):
    if seconds < 0:
        return "-" + fmt_duration(-seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    else:
        return "%02d:%02d" % (minutes, seconds)


def fmt_time_relative(seconds):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc

    Adapted from https://stackoverflow.com/a/1551394/6160055
    """

    now = datetime.now()
    if isinstance(seconds, (int, float)):
        seconds = datetime.fromtimestamp(seconds)

    diff = now - seconds
    second_diff = diff.seconds
    day_diff = diff.days

    assert day_diff >= 0

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + "s ago"
        if second_diff < 120:
            return f"1m {second_diff % 60}s ago"
        if second_diff < 3600:
            return str(second_diff // 60) + "m ago"
        if second_diff < 7200:
            return f"1h {second_diff % 3600 // 60}m ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + "h ago"
    if day_diff <= 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"


def fmt_time_absoulte(seconds):
    now = datetime.now()
    if isinstance(seconds, (int, float)):
        seconds = datetime.fromtimestamp(seconds)

    diff = now - seconds
    day_diff = diff.days

    assert day_diff >= 0

    if day_diff == 0:
        return f"at {seconds.strftime('%H:%M')}"
    if day_diff == 1:
        return f"Yest at {seconds.strftime('%H:%M')}"
    if day_diff < 7:  # e.g. Tue at 12:34
        return f"{seconds.strftime('%a')} at {seconds.strftime('%H:%M')}"
    # Same month: Tue 12 at 12:34
    if day_diff < 31 and now.month == seconds.month:
        return f"{seconds.strftime('%a %d')} at {seconds.strftime('%H:%M')}"
    # Same year: Tue 12 Jan at 12:34
    if now.year == seconds.year:
        return f"{seconds.strftime('%a %d %b')} at {seconds.strftime('%H:%M')}"
    # Full date: Tue 12 Jan 2023 at 12:34
    return f"{seconds.strftime('%a %d %b %Y')} at {seconds.strftime('%H:%M')}"


def fmt_time(seconds, relative=True):
    return fmt_time_relative(seconds) if relative else fmt_time_absoulte(seconds)


def shorten(text: str, max_len: int) -> str:
    """Shorten a text to max_len characters, adding ... if necessary."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."  # 3 for the ...


def color_from_name(name: str) -> tuple[int, int, int]:
    instance = random.Random(name)
    return instance.randint(0, 255), instance.randint(0, 255), instance.randint(0, 255)


def blit_aligned(
    surf: pygame.Surface,
    to_blit: pygame.Surface,
    y: int,
    align: int = pg.FONT_LEFT,
    left: int | None = None,
    right: int | None = None,
) -> pygame.Rect:
    if left is None:
        left = 0
    if right is None:
        right = surf.get_width()

    if align == pg.FONT_LEFT:
        return surf.blit(to_blit, (left, y))
    elif align == pg.FONT_RIGHT:
        return surf.blit(to_blit, (right - to_blit.get_width(), y))
    elif align == pg.FONT_CENTER:
        return surf.blit(to_blit, ((left + right - to_blit.get_width()) // 2, y))
    else:
        raise ValueError(f"Invalid alignment: {align}")


class DFont:
    def __init__(self, path: Path):
        self.path = path
        self.by_size: dict[tuple, pygame.Font] = {}

    def get_font(self, size: int, align: int = pg.FONT_LEFT) -> pygame.Font:
        key = size, align
        if key not in self.by_size:
            self.by_size[key] = pygame.Font(self.path, size)
            self.by_size[key].align = align
        return self.by_size[key]

    def render(
        self,
        text: str,
        size: int | tuple[int, int],
        color: tuple,
        monospaced_time: bool = False,
        align: int = pg.FONT_LEFT,
    ):
        if not isinstance(size, int):
            if monospaced_time:
                # Use the font size that fits a text equivalent to the time.
                # We use 0s to make sure the text is as wide as possible and doesn't jitter.
                size = self.auto_size(re.sub(r"\d", "0", text), size)
            else:
                size = self.auto_size(text, size)

        font = self.get_font(size, align)

        sizing = self.tight_size_with_newlines(text, size)

        if not monospaced_time:
            surf = font.render(text, True, color)
            surf = surf.subsurface(
                (0, -sizing.y_offset, surf.get_width(), min(sizing.height, surf.get_height()))
            )
            return surf

        else:
            digits = "0123456789"
            # We render each char independently to make sure they are monospaced.
            chars = [font.render(c, True, color) for c in text]
            # Make each digit the size of a 0.
            width = font.size("0")[0]
            full_width = sum(
                s.get_width() if c not in digits else width for c, s in zip(text, chars)
            )

            # Create a surface with the correct width.
            surf = pygame.Surface((full_width, sizing.height), pg.SRCALPHA)
            # Blit each char at the correct position.
            x = 0
            for c, s in zip(text, chars):
                if c in digits:
                    blit_x = x + (width - s.get_width()) // 2
                else:
                    blit_x = x

                surf.blit(s, (blit_x, sizing.y_offset))
                x += s.get_width() if c not in digits else width

            # If \ is pressed, show the metrics of the text.
            if pygame.key.get_pressed()[pg.K_BACKSLASH]:
                pygame.draw.rect(surf, (0, 255, 0), (0, 0, surf.get_width(), surf.get_height()), 1)

            return surf

    @dataclass
    class TextSize:
        width: int
        height: int
        y_offset: int

    def tight_size_with_newlines(self, text: str, size: int) -> TextSize:
        """Return the size of the text with newlines and if single line, without the extra space around it."""
        lines = text.splitlines()
        font = self.get_font(size)
        line_height = font.get_height()
        if not lines:
            return self.TextSize(0, line_height, 0)
        elif len(lines) == 1:
            # If there is only one line, we can use the metrics to get the visible height,
            # with much less space around the text. This is especially relevant for Bevan.
            metrics = [m for m in font.metrics(text) if m is not None]
            min_y = min(m[2] for m in metrics)
            max_y = max(m[3] for m in metrics)
            line_height = max_y - min_y
            return self.TextSize(font.size(text)[0], line_height, -font.get_ascent() + max_y)
        else:
            return self.TextSize(
                max(font.size(line)[0] for line in lines),
                line_height * text.count("\n") + line_height,
                0,
            )

    def auto_size(self, text: str, max_rect: tuple[int, int]):
        """Find the largest font size that will fit text in max_rect."""
        # Use dichotomy to find the largest font size that will fit text in max_rect.

        min_size = 1
        max_size = max_rect[1]
        while min_size < max_size:
            font_size = (min_size + max_size) // 2
            text_size = self.tight_size_with_newlines(text, font_size)

            if text_size.width <= max_rect[0] and text_size.height <= max_rect[1]:
                min_size = font_size + 1
            else:
                max_size = font_size
        return min_size - 1

    def table(
        self,
        rows: list[list[str]],
        size: int | tuple[int, int],
        color: tuple[int, int, int] | list[tuple[int, int, int]],
        title: str | None = None,
        col_sep: str = "__",
        align: int | list[int] = pg.FONT_LEFT,
        title_color: tuple[int, int, int] | None = None,
        title_align: int = pg.FONT_CENTER,
        hidden_rows: list[list[str]] = [],
        header_line_color: tuple[int, int, int] | None = None,
    ):
        """Render a table with the given rows and size.

        Args:
            rows: The rows of the table.
            size: The font size of the table. If this is a tuple, the table is the largest that can fit in this (width, height).
            color: The text color of each column. If this is a tuple, it is used for all columns.
            title: The optional title of the table.
            col_sep: Text whose width will be used to separate columns.
            align: The alignment of each column. If this is an int, it is be used for all columns.
            title_color: The color of the title. If omitted, the color of the first column is be used.
            hidden_rows: Rows that are not rendered, but are used to size the table. Prevents change of size when scrolling.
            header_line_color: Draw a line after the first row with this color.
        """
        assert rows

        cols = list(zip(*rows, strict=True))

        if isinstance(align, int):
            align = [align] * len(cols)
        if isinstance(color, tuple):
            color = [color] * len(cols)
        assert len(align) == len(cols)
        assert len(color) == len(cols)
        if title_color is None:
            title_color = color[0]

        # It's a bit hard to size a table, we do it by creating a dummy text
        # block that has the same size.
        dummy_font = self.get_font(10)  # len() is not a good proxy for visual size.
        cols_with_hidden = list(zip(*rows, *hidden_rows, strict=True))
        longest_by_col = [max(col, key=lambda x: dummy_font.size(x)[0]) for col in cols_with_hidden]
        long_line = col_sep.join(longest_by_col)
        dummy_long_content = "\n".join([long_line] * len(rows))
        if title:
            dummy_long_content = title + "\n" + dummy_long_content

        if not isinstance(size, int):
            size = self.auto_size(dummy_long_content, size)

        font = self.get_font(size)
        surf = font.render(dummy_long_content, True, (0, 0, 0))
        surf.fill((0, 0, 0, 0))

        # Draw title
        if title:
            title_surf = font.render(title, True, title_color)
            y = blit_aligned(surf, title_surf, 0, title_align).bottom
        else:
            y = 0

        sep_width = font.size(col_sep)[0]
        column_widths = [font.size(longest)[0] for longest in longest_by_col]

        # Render each column
        x = 0
        for col, align, col_color, width in zip(cols, align, color, column_widths):
            col_surf = self.get_font(size, align).render("\n".join(col), True, col_color)
            blit_aligned(surf, col_surf, y, align, x, x + width)
            x += width + sep_width

        # Draw a line under the header
        if header_line_color is not None:
            y += font.get_height()
            pygame.draw.line(surf, header_line_color, (0, y), (surf.get_width(), y), 1)

        return surf


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
       
    set_window_to_float()



def play(sound):
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()


def split_rect(rect, *ratios, horizontal: bool = False):
    """Split a rect vertically in ratios."""
    total_ratio = sum(ratios)
    ratios = [r / total_ratio for r in ratios]
    cummulative_ratios = [0] + [sum(ratios[:i]) for i in range(1, len(ratios) + 1)]
    if horizontal:
        xs = [rect.left + int(rect.width * r) for r in cummulative_ratios]
        return [
            pygame.Rect(xs[i], rect.top, xs[i + 1] - xs[i], rect.height) for i in range(len(ratios))
        ]
    else:
        ys = [rect.top + int(rect.height * r) for r in cummulative_ratios]
        return [
            pygame.Rect(rect.left, ys[i], rect.width, ys[i + 1] - ys[i]) for i in range(len(ratios))
        ]


def human_duration(duration: str) -> int:
    """Convert a human duration to seconds."""

    if duration.startswith("-"):
        return -human_duration(duration[1:])

    # Parse the duration.
    total = 0
    multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    for part in duration.split():
        try:
            total += int(part[:-1]) * multiplier[part[-1]]
        except (ValueError, KeyError):
            raise ValueError(f"Invalid duration part: {part}")

    return total


@dataclass
class Purpose:
    text: str
    timestamp: float = dataclasses.field(default_factory=time)

    def add_to_history(self, history_file: Path):
        with history_file.open("a") as f:
            f.write(json.dumps(self.__dict__) + "\n")


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

        rects = {k: rect for k, rect in zip(layout.keys(), split_rect(screen, *layout.values()))}

        # Bottom has horizontal layout with [total_time | purpose_time]
        if total_time_rect := rects.pop("totals", None):
            rects["total_time"], _, rects["purpose_time"] = split_rect(
                total_time_rect, 1, 0.2, 1, horizontal=True
            )

        return rects


class CountdownCallback:
    """Call a command once the timer goes below a specific time."""

    def __init__(self, time_and_command: str) -> None:
        time, _, command = time_and_command.partition(":")
        self.command = command
        if isinstance(time, str):
            self.time = human_duration(time)
        else:
            self.time = time
        self.executed = False

    def update(self, current_time: float):
        """Call the command if needed. Current time is the number of seconds on screen."""
        if current_time >= self.time:
            self.executed = False
        elif not self.executed:
            self.executed = True
            # Asynchronously run the command.
            print(f"Running: {self.command}")
            subprocess.Popen(self.command, shell=True)


app = typer.Typer(add_completion=False)


def StyleOpt(help=None, **kwargs):
    return Option(help=help, rich_help_panel="Style", **kwargs)


@app.command(
    help="Stay on task with PUCOTI, a countdown timer built for simplicity and purpose.\n\nGUI Shortcuts:\n\n"
    + SHORTCUTS.replace("\n", "\n\n")
)
def main(
    # fmt: off
    initial_timer: Annotated[str, Argument(help="The initial timer duration.")] = "5m",
    bell: Annotated[Path, Option(help="Path to the bell sound file.")] = BELL,
    ring_every: Annotated[int, Option(help="The time between rings, in seconds.")] = 20,
    ring_count: Annotated[int, Option(help="Number of rings played when the time is up.")] = -1,
    restart: Annotated[bool, Option(help="Restart the timer when it reaches 0.")] = False,
    run_at: Annotated[list[str], Option(help="Run a command at a specific time. Example: --run-at '-1m 30s:notify-send \"Time was up 1m30s ago!\"'")] = [],
    timer_font: Annotated[Path, StyleOpt("Path to the font for the timer.")] = BIG_FONT,
    font: Annotated[Path, StyleOpt("Path to the font for all other text.")] = FONT,
    background_color: Annotated[tuple[int, int, int], StyleOpt()] = (0, 0, 0),
    timer_color: Annotated[tuple[int, int, int], StyleOpt()] = (255, 224, 145),
    timer_up_color: Annotated[tuple[int, int, int], StyleOpt()] = (255, 0, 0),
    purpose_color: Annotated[tuple[int, int, int], StyleOpt()] = (183, 255, 183),
    total_time_color: Annotated[tuple[int, int, int], StyleOpt()] = (183, 183, 255),
    window_position: tuple[int, int] = (-5, -5),
    window_size: tuple[int, int] = (220, 80),
    history_file: Annotated[Path, Option(help="Path to the file where the purpose history is stored.")] = Path("~/.pucoti_history"),
    # fmt: on
) -> None:

    history_file = history_file.expanduser()
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_file.touch(exist_ok=True)

    pygame.init()
    pygame.mixer.init()
    pygame.key.set_repeat(300, 20)

    window = sdl2.Window("PUCOTI", window_size, borderless=True, always_on_top=True, resizable=True)
    window.get_surface().fill((0, 0, 0))
    window.flip()

    screen = window.get_surface()
    clock = pygame.time.Clock()
    big_font = DFont(timer_font)
    normal_font = DFont(font)

    position = 0
    place_window(window, *window_position)

    initial_duration = human_duration(initial_timer)
    start = round(time())
    timer = initial_duration
    last_rung = 0
    nb_rings = 0
    callbacks = [CountdownCallback(time_and_command) for time_and_command in run_at]

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
            elif event.type == pg.KEYDOWN:
                if scene == Scene.HELP:
                    scene = Scene.MAIN
                elif scene == Scene.ENTERING_PURPOSE:
                    if event.key == pg.K_BACKSPACE:
                        purpose = purpose[:-1]
                    elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_ESCAPE):
                        scene = Scene.MAIN
                    elif event.unicode:
                        purpose += event.unicode
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
                    timer -= 60
                elif event.key == pg.K_k:
                    timer += 60
                elif event.key == pg.K_r:
                    # +0.5 to show visually round time -> more satisfying
                    timer = initial_duration + (round(time() + 0.5) - start)
                elif event.key == pg.K_MINUS:
                    window.size = (window.size[0] / WINDOW_SCALE, window.size[1] / WINDOW_SCALE)
                elif event.key == pg.K_PLUS or event.key == pg.K_EQUALS:
                    window.size = (window.size[0] * WINDOW_SCALE, window.size[1] * WINDOW_SCALE)
                elif event.key == pg.K_p:
                    position = (position + 1) % len(POSITIONS)
                    place_window(window, *POSITIONS[position])
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

        screen.fill(background_color)

        # Render purpose, if there is space.
        if purpose_rect := layout.get("purpose"):
            t = normal_font.render(purpose, purpose_rect.size, purpose_color)
            r = screen.blit(t, t.get_rect(center=purpose_rect.center))
            if scene == Scene.ENTERING_PURPOSE and (time() % 1) < 0.7:
                if r.height == 0:
                    r.height = purpose_rect.height
                if r.right >= purpose_rect.right:
                    r.right = purpose_rect.right - 3
                pygame.draw.line(screen, purpose_color, r.topright, r.bottomright, 2)

        # Render time.
        if time_rect := layout.get("time"):
            remaining = timer - (time() - start)
            color = timer_up_color if remaining < 0 else timer_color
            t = big_font.render(
                fmt_duration(abs(remaining)), time_rect.size, color, monospaced_time=True
            )
            screen.blit(t, t.get_rect(center=time_rect.center))

        if total_time_rect := layout.get("total_time"):
            t = normal_font.render(
                fmt_duration(time() - start),
                total_time_rect.size,
                total_time_color,
                monospaced_time=True,
            )
            screen.blit(t, t.get_rect(midleft=total_time_rect.midleft))

        if purpose_time_rect := layout.get("purpose_time"):
            t = normal_font.render(
                fmt_duration(time() - purpose_start_time),
                purpose_time_rect.size,
                purpose_color,
                monospaced_time=True,
            )
            screen.blit(t, t.get_rect(midright=purpose_time_rect.midright))

        if help_rect := layout.get("help"):
            title = "PICOTI Bindings"
            s = normal_font.table(
                [line.split(": ") for line in SHORTCUTS.split("\n")],  # type: ignore
                help_rect.size,
                [purpose_color, timer_color],
                title=title,
                col_sep=": ",
                align=[pg.FONT_RIGHT, pg.FONT_LEFT],
                title_color=timer_color,
            )
            screen.blit(s, s.get_rect(center=help_rect.center))

        if purpose_history_rect := layout.get("purpose_history"):
            timestamps = [p.timestamp for p in purpose_history] + [time()]
            rows = [
                [
                    fmt_duration(end_time - p.timestamp),
                    shorten(p.text, 40),
                    fmt_time(p.timestamp, relative=show_relative_time),
                ]
                for p, end_time in zip(purpose_history, timestamps[1:], strict=True)
                if p.text
            ]
            first_shown = len(rows) - history_lines - history_scroll
            last_shown = len(rows) - history_scroll
            hidden_rows = rows[:first_shown] + rows[last_shown:]
            rows = rows[first_shown:last_shown]

            headers = ["Span", "Purpose [J/K]", "Started [L]"]
            s = normal_font.table(
                [headers] + rows,
                purpose_history_rect.size,
                [total_time_color, purpose_color, timer_color],
                title="History",
                col_sep=": ",
                align=[pg.FONT_RIGHT, pg.FONT_LEFT, pg.FONT_RIGHT],
                title_color=purpose_color,
                hidden_rows=hidden_rows,
                header_line_color=purpose_color,
            )
            screen.blit(s, s.get_rect(center=purpose_history_rect.center))

        # If \ is pressed, show the rects in locals()
        if pygame.key.get_pressed()[pg.K_BACKSLASH]:
            debug_font = normal_font.get_font(20)
            for name, rect in locals().items():
                if isinstance(rect, pygame.Rect):
                    color = color_from_name(name)
                    pygame.draw.rect(screen, color, rect, 1)
                    # and its name
                    t = debug_font.render(name, True, (255, 255, 255))
                    screen.blit(t, rect.topleft)

        # Ring the bell if the time is up.
        if remaining < 0 and time() - last_rung > ring_every and nb_rings != ring_count:
            last_rung = time()
            nb_rings += 1
            play(bell)
            if restart:
                timer = initial_duration + (round(time() + 0.5) - start)

        elif remaining > 0:
            nb_rings = 0

        # And execute the callbacks.
        for callback in callbacks:
            callback.update(timer - (time() - start))

        window.flip()
        clock.tick(30)


if __name__ == "__main__":
    app()
