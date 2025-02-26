import pygame.locals as pg
import luckypot

from .base_screen import PucotiScreen
from . import main_screen


class StartScreen(PucotiScreen):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.timer = 0

    def logic(self):
        super().logic()

        self.timer += 1
        if self.timer > 20:
            self.replace_state(main_screen.MainScreen(self.ctx))

    def handle_events(self, events):
        super().handle_events(events)
        for event in events:
            if event.type == pg.KEYDOWN:
                self.replace_state(main_screen.MainScreen(self.ctx))

    def draw(self, gfx: luckypot.GFX):
        super().draw(gfx)
        r = gfx.surf.get_rect()
        r.inflate_ip(-10, -10)
        s = self.ctx.config.font.big.render(
            "PUCOTI",
            r.size,
            self.ctx.config.color.timer,
            align=pg.FONT_CENTER,
        )
        gfx.blit(s, center=r.center)
