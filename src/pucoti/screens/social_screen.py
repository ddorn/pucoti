from time import time
from luckypot import GFX
import pygame

from pucoti.widgets.sentence_edit import SentenceEdit, Field

from .base_screen import PucotiScreen
from ..pygame_utils import split_rect
from ..time_utils import fmt_duration


class SocialLoginScreen(PucotiScreen):
    MUST_BE_BIG_WINDOW = True

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.login_edit = SentenceEdit(
            [
                "Join ",
                Field("room", self.ctx.config.social.room, self.config.color.purpose),
                " as ",
                Field("name", self.ctx.config.social.username, self.config.color.purpose),
                ".",
            ],
            self.config.color.timer,
            font=self.ctx.config.font.normal,
            help_text="CTRL+ENTER to join",
            submit_callback=self.join_callback,
        )

    def logic(self):
        super().logic()
        if self.ctx.config.social.enabled:
            self.replace_state(SocialScreen(self.ctx))

    def join_callback(self, data: dict[str, str]):
        self.ctx.config.social.username = data["name"].strip()
        self.ctx.config.social.room = data["room"].strip()
        self.ctx.config.social.enabled = True

    def draw(self, gfx: GFX):
        super().draw(gfx)
        self.login_edit.draw(gfx, self.layout()["main"])

    def handle_event(self, event) -> bool:
        if super().handle_event(event):
            return True

        if self.login_edit.handle_event(event):
            return True


class SocialScreen(PucotiScreen):
    MUST_BE_BIG_WINDOW = True

    def __init__(self, ctx) -> None:
        super().__init__(ctx)

        self.vertical = False

    def logic(self):
        super().logic()

        if not self.ctx.config.social.enabled:
            self.replace_state(SocialLoginScreen(self.ctx))
            return

    def layout(self):
        layout = super().layout()
        rect = layout["main"]

        timers_rect, room_rect, exit_rect = split_rect(rect, 1, 0.2, 0.1)
        layout["timers"] = timers_rect
        layout["room"] = room_rect
        layout["exit"] = exit_rect

        # Split the rect into n sub-rect
        n = len(self.ctx.friend_activity)
        if n >= 2:
            new = split_rect(timers_rect, *[1] * n, horizontal=not self.vertical, spacing=0.1)
            for i, r in enumerate(new):
                layout[i] = r
        return layout

    def layout_one(self, rect: pygame.Rect):
        user, time = split_rect(rect, 1, 2)
        # total, _, purpose_total = split_rect(totals, 1, 0.2, 1, horizontal=True)
        return user, time  # , total, purpose_total

    def draw(self, gfx: GFX):
        super().draw(gfx)

        layout = self.layout()
        font = self.ctx.config.font.normal
        room = self.ctx.config.social.room

        if len(self.ctx.friend_activity) == 0:
            text = [("You're not online. Yet?", self.config.color.purpose)]
        elif len(self.ctx.friend_activity) == 1:
            text = [
                ("You're alone. Tell your friends to join ", self.config.color.timer),
                (room, self.config.color.purpose),
                (".", self.config.color.timer),
            ]
        else:
            text = [
                ("Tell your friends to join ", self.config.color.timer),
                (room, self.config.color.purpose),
                (".", self.config.color.timer),
            ]

        surf, rects, font_size = font.render_parts(
            text, layout["room"].size, align=pygame.FONT_CENTER
        )
        room_rect = gfx.blit(surf, center=layout["room"].center)
        # Show "Ctrl+Enter to exit" in the bottom right corner
        exit_text = "CTRL+ENTER to exit"
        surf = font.render(exit_text, font_size // 3, self.config.color.timer)
        gfx.blit(surf, topright=room_rect.bottomright)

        if len(self.ctx.friend_activity) < 2:
            return

        for i, friend in enumerate(self.ctx.friend_activity):
            rect = layout[i]
            if friend.purpose:
                text = f"{friend.username}: {friend.purpose}"
            else:
                text = friend.username
            remaining = friend.timer_end - (time() - friend.start)

            user_r, time_r = self.layout_one(rect)
            # user_r, time_r, total_r, purpose_total_r = self.layout_one(rect)

            gfx.blit(
                font.render(text, user_r.size, self.config.color.purpose, monospaced_time=True),
                center=user_r.center,
            )
            gfx.blit(
                font.render(
                    fmt_duration(remaining),
                    time_r.size,
                    self.config.color.timer,
                    monospaced_time=True,
                ),
                center=time_r.center,
            )
            # gfx.blit(
            #     font.render(
            #         fmt_duration(time() - friend.start),
            #         total_r.size,
            #         self.config.color.total_time,
            #     ),
            #     midleft=total_r.midleft,
            # )
            # if friend.purpose_start:
            #     gfx.blit(
            #         font.render(
            #             fmt_duration(time() - friend.purpose_start),
            #             purpose_total_r.size,
            #             self.config.color.purpose,
            #         ),
            #         midright=purpose_total_r.midright,
            #     )

    def handle_event(self, event) -> bool:
        if super().handle_event(event):
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v:
                self.vertical = not self.vertical
                return True
            elif event.key == pygame.K_RETURN and event.mod & pygame.KMOD_CTRL:
                self.ctx.config.social.enabled = False
                self.replace_state(SocialLoginScreen(self.ctx))
                return True

        return False
