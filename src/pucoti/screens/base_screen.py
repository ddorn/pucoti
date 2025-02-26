import luckypot
import pygame.locals as pg


from ..context import Context


class PucotiScreen(luckypot.AppState):
    FPS = 30

    def __init__(self, ctx: Context):
        self.ctx = ctx
        super().__init__()

    @property
    def config(self):
        return self.ctx.config

    def draw(self, gfx: luckypot.GFX):
        super().draw(gfx)
        gfx.fill(self.config.color.background)

    def logic(self):
        return super().logic()

    def available_rect(self):
        width, height = self.ctx.app.window.size
        screen = pg.Rect(0, 0, width, height)

        if width > 200:
            screen = screen.inflate(-width // 10, 0)

        return screen
