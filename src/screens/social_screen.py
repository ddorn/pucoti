from time import time
from luckypot import GFX
import pygame

from .base_screen import PucotiScreen
from ..pygame_utils import split_rect
from ..time_utils import fmt_duration


class SocialScreen(PucotiScreen):

    def __init__(self) -> None:
        super().__init__()

        self.vertical = True

    def layout(self, n: int):
        r = self.available_rect()

        # Split the rect into n sub-rect
        return split_rect(r, *[1] * n, horizontal=not self.vertical, spacing=0.1)

    def layout_one(self, rect: pygame.Rect):
        user, time = split_rect(rect, 1, 2)
        # total, _, purpose_total = split_rect(totals, 1, 0.2, 1, horizontal=True)
        return user, time  # , total, purpose_total

    def draw(self, gfx: GFX):
        super().draw(gfx)

        font = self.ctx.config.font.normal

        if len(self.ctx.friend_activity) < 2:
            if len(self.ctx.friend_activity) == 1:
                text = "No friends are currently active."
            elif not self.ctx.config.social.enabled:
                text = "Use --social name@room to enable social features."
            else:
                text = "You're not online."
            rect = self.available_rect()
            gfx.blit(font.render(text, rect.size, self.config.color.purpose), center=rect.center)
            return

        for friend, rect in zip(
            self.ctx.friend_activity, self.layout(len(self.ctx.friend_activity))
        ):
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
            else:
                self.pop_state()
            return True

        return False
