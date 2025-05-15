from time import time

from luckypot.gfx import GFX
import pygame as pg

from .. import time_utils, pygame_utils
from .base_screen import PucotiScreen


class PurposeHistoryScreen(PucotiScreen):
    MUST_BE_BIG_WINDOW = True

    def __init__(self, ctx) -> None:
        super().__init__(ctx)

        self.history_lines = 10
        self.history_scroll = 0  # From the bottom
        self.show_relative_time = True

    def handle_event(self, event) -> bool:
        if super().handle_event(event):
            return True

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_j:
                self.history_scroll = max(0, self.history_scroll - 1)
            elif event.key == pg.K_k:
                self.history_scroll = min(
                    len([p for p in self.ctx.purpose_history if p.text]) - self.history_lines,
                    self.history_scroll + 1,
                )
            elif event.key == pg.K_s:
                self.show_relative_time = not self.show_relative_time
            else:
                self.pop_state()
            return True

        return False

    def draw(self, gfx: GFX):
        super().draw(gfx)

        rect = self.layout()["main"]
        timestamps = [p.timestamp for p in self.ctx.purpose_history] + [time()]
        rows = [
            [
                time_utils.fmt_duration(end_time - p.timestamp),
                pygame_utils.shorten(p.text, 40),
                time_utils.fmt_time(p.timestamp, relative=self.show_relative_time),
            ]
            for p, end_time in zip(self.ctx.purpose_history, timestamps[1:], strict=True)
            if p.text
        ]
        first_shown = len(rows) - self.history_lines - self.history_scroll
        last_shown = len(rows) - self.history_scroll
        hidden_rows = rows[:first_shown] + rows[last_shown:]
        rows = rows[first_shown:last_shown]

        headers = ["Span", "Purpose [J/K]", "Started [S]"]
        s = self.config.font.normal.table(
            [headers] + rows,
            rect.size,
            [self.config.color.total_time, self.config.color.purpose, self.config.color.timer],
            title="History",
            col_sep=": ",
            align=[pg.FONT_RIGHT, pg.FONT_LEFT, pg.FONT_RIGHT],
            title_color=self.config.color.purpose,
            hidden_rows=hidden_rows,
            header_line_color=self.config.color.purpose,
        )
        gfx.blit(s, center=rect.center)
