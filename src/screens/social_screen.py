from luckypot import GFX
import pygame

from .base_screen import PucotiScreen
from ..pygame_utils import split_rect


class SocialScreen(PucotiScreen):

    def layout(self, n: int):
        r = self.available_rect()

        # Split the rect into n sub-rect
        return split_rect(r, *[1] * n, horizontal=False)

    def draw(self, gfx: GFX):
        super().draw(gfx)

        font = self.ctx.config.font.normal

        if len(self.ctx.friend_activity) < 2:
            text = "No friends are currently active."
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

            gfx.blit(font.render(text, rect.size, self.config.color.purpose), center=rect.center)

    def handle_event(self, event) -> bool:
        if super().handle_event(event):
            return True

        if event.type == pygame.KEYDOWN:
            self.pop_state()
            return True

        return False
