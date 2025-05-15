from luckypot.gfx import GFX
import pygame as pg

from .. import constants
from .base_screen import PucotiScreen


class HelpScreen(PucotiScreen):
    MUST_BE_BIG_WINDOW = True

    def handle_event(self, event) -> bool:
        if super().handle_event(event):
            return True

        if event.type == pg.KEYDOWN:
            self.pop_state()
            return True

        return False

    def draw(self, gfx: GFX):
        super().draw(gfx)
        rect = self.layout()["main"]

        title = "PUCOTI Bindings"
        s = self.config.font.normal.table(
            [line.split(": ") for line in constants.SHORTCUTS.split("\n")],  # type: ignore
            rect.size,
            [self.config.color.purpose, self.config.color.timer],
            title=title,
            col_sep=": ",
            align=[pg.FONT_RIGHT, pg.FONT_LEFT],
            title_color=self.config.color.timer,
        )
        gfx.blit(s, center=rect.center)
