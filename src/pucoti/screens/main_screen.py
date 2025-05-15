from time import time

import pygame
import pygame.locals as pg

from .. import time_utils
from .. import pygame_utils
from .. import constants
from .base_screen import PucotiScreen
from . import help_screen, purpose_history_screen, social_screen
from ..context import Context
from ..widgets.text_edit import TextEdit


class MainScreen(PucotiScreen):
    def __init__(self, ctx: Context) -> None:
        super().__init__(ctx)

        self.hide_totals = False

        self.last_purpose = ctx.purpose
        self.purpose_editor = TextEdit(
            initial_value=ctx.purpose_history[-1].text,
            color=ctx.config.color.purpose,
            font=ctx.config.font.normal,
            submit_callback=ctx.set_purpose,
            autofocus=True,
        )

        self.last_mouse_move = 0.0
        self.buttons: dict[str, pygame.Rect] = {}

    @property
    def timer_end(self):
        return self.ctx.timer_end

    def on_exit(self):
        self.ctx.set_purpose("")

    def paused_logic(self):
        self.ctx.ring_if_needed()
        self.ctx.update_servers(force=False)

        # Update purpose editor if purpose changed externally (e.g. from the controller).
        if self.ctx.purpose != self.last_purpose:
            self.last_purpose = self.ctx.purpose
            self.purpose_editor.text = self.ctx.purpose

        return super().paused_logic()

    def logic(self):
        self.paused_logic()
        return super().logic()

    def handle_event(self, event) -> bool:
        if self.purpose_editor.handle_event(event):
            return True

        if event.type == pg.MOUSEMOTION:
            self.last_mouse_move = time()

        elif event.type == pg.KEYDOWN:

            # We only handle keydown events from here on.
            match event.key:
                case pg.K_j:
                    delta = -60 * 5 if pygame_utils.shift_is_pressed(event) else -60
                    self.ctx.shift_timer(delta)
                case pg.K_k:
                    delta = 60 * 5 if pygame_utils.shift_is_pressed(event) else 60
                    self.ctx.shift_timer(delta)
                case number if number in constants.NUMBER_KEYS:
                    new_duration = 60 * pygame_utils.get_number_from_key(number)
                    if pygame_utils.shift_is_pressed(event):
                        new_duration *= 10
                    self.ctx.set_timer_to(new_duration)
                    self.ctx.initial_duration = new_duration
                case pg.K_r:
                    self.ctx.set_timer_to(self.ctx.initial_duration)
                case pg.K_t:
                    self.hide_totals = not self.hide_totals
                case pg.K_h | pg.K_QUESTION:
                    self.push_state(help_screen.HelpScreen(self.ctx))
                case pg.K_l:
                    self.push_state(purpose_history_screen.PurposeHistoryScreen(self.ctx))
                case pg.K_s:
                    self.push_state(social_screen.SocialScreen(self.ctx))
                case pg.K_ESCAPE:
                    self.ctx.app.make_window_small()
                case _:
                    return super().handle_event(event)
            return True

        else:
            return super().handle_event(event)

    def layout(self):
        base_layout = super().layout()
        rect = base_layout["main"]
        height = rect.height

        if self.purpose_editor.editing:
            if height < 60:
                layout = {"purpose": 1}
            elif height < 80:
                layout = {"purpose": 2, "time": 1}
            else:
                layout = {"purpose": 2, "time": 1, "totals": 0.5}
        else:
            if height < 60:
                layout = {"time": 1}
            elif height < 80:
                layout = {"purpose": 1, "time": 2}
            else:
                layout = {"purpose": 1, "time": 2, "totals": 1}

            if not self.ctx.purpose:
                layout["time"] += layout.pop("purpose", 0)

        if self.hide_totals:
            layout.pop("totals", None)

        rects = {
            k: rect
            for k, rect in zip(layout.keys(), pygame_utils.split_rect(rect, *layout.values()))
        }

        # Bottom has horizontal layout with [total_time | purpose_time]
        if total_time_rect := rects.pop("totals", None):
            rects["total_time"], _, rects["purpose_time"] = pygame_utils.split_rect(
                total_time_rect, 1, 0.2, 1, horizontal=True
            )

        return {
            **base_layout,
            **rects,
        }

    def draw(self, gfx: help_screen.GFX):
        super().draw(gfx)
        layout = self.layout()

        if time_rect := layout.get("time"):
            remaining = self.ctx.remaining_time  # locked
            color = self.config.color.timer_up if remaining < 0 else self.config.color.timer
            self.show_timer(gfx, abs(remaining), color, time_rect, "center", "Main timer")

        if total_time_rect := layout.get("total_time"):
            self.show_timer(
                gfx,
                time() - self.ctx.start,
                self.config.color.total_time,
                total_time_rect,
                "midleft",
                "Time on pucoti",
            )

        if purpose_time_rect := layout.get("purpose_time"):
            self.show_timer(
                gfx,
                time() - self.ctx.purpose_start_time,
                self.config.color.purpose,
                purpose_time_rect,
                "midright",
                "Time on purpose",
            )

        if purpose_rect := layout.get("purpose"):
            self.purpose_editor.draw(gfx, purpose_rect)

    def show_timer(self, gfx, value: float, color, rect, anchor: str, label: str):
        """Show the timer in the given rect and anchor."""

        mouse_pos = pygame.mouse.get_pos()
        if rect.collidepoint(mouse_pos) and time() - self.last_mouse_move < 0.4:
            text = label
        else:
            text = time_utils.fmt_duration(value)

        t = self.config.font.big.render(
            text,
            rect.size,
            color,
            monospaced_time=True,
        )

        anchor_data = {anchor: getattr(rect, anchor)}
        return gfx.blit(t, **anchor_data)
