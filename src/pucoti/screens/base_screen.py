import luckypot
import pygame
import pygame.locals as pg

from ..context import Context
from ..assets import load_icon


class PucotiScreen(luckypot.AppState):
    FPS = 30
    MUST_BE_BIG_WINDOW = False

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.buttons: dict[str, pygame.Rect] = {}
        super().__init__()

    def on_enter(self):
        super().on_enter()

        if self.MUST_BE_BIG_WINDOW:
            self.ctx.app.make_window_big()

    @property
    def config(self):
        return self.ctx.config

    def draw(self, gfx: luckypot.GFX):
        super().draw(gfx)
        gfx.fill(self.config.color.background)

        self.buttons.clear()

        layout = self.layout()
        if top_bar := layout.get("top_bar"):
            mouse = pygame.mouse.get_pos()
            if top_bar.collidepoint(mouse):
                color = self.config.color.timer
            else:
                color = "#666666"

            buttons = {
                "home": "home",
                "history": "list",
                "social": "users",
                "help": "help-circle",
                # "settings": "settings",
            }
            top_bar.inflate_ip(-30, -10)

            space_x = 24 + 16
            for i, (button, icon_name) in enumerate(reversed(buttons.items())):
                x = top_bar.right - i * space_x
                icon = load_icon(icon_name, color)
                r = icon.get_rect(midright=(x, top_bar.centery))
                if r.collidepoint(mouse):
                    icon = load_icon(icon_name, self.config.color.purpose)
                gfx.blit(icon, topleft=r.topleft)
                self.buttons[button] = r

    def logic(self):
        return super().logic()

    def handle_event(self, event) -> bool:
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for button, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.switch_to(button)
                    return True

        return super().handle_event(event)

    def switch_to(self, state_name: str):
        from . import main_screen, help_screen, purpose_history_screen, social_screen

        states = {
            "home": main_screen.MainScreen,
            "help": help_screen.HelpScreen,
            "history": purpose_history_screen.PurposeHistoryScreen,
            "settings": social_screen.SocialScreen,
            "social": social_screen.SocialScreen,
        }

        target = states[state_name]
        if isinstance(self, target):
            return

        if isinstance(self, main_screen.MainScreen):
            self.push_state(target(self.ctx))
        else:
            self.replace_state(target(self.ctx))

    def layout(self):
        width, height = self.ctx.app.window.size
        screen = pg.Rect(0, 0, width, height)

        if width > 200:
            screen = screen.inflate(-width // 10, 0)

        rects = dict(main=screen)

        if height > 140:
            bar_height = 40
            screen.height -= bar_height
            screen.y += bar_height
            rects["top_bar"] = pg.Rect(0, 0, width, bar_height)

        return rects
