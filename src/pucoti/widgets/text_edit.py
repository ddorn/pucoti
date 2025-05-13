import re
from time import time
from typing import Callable

import pygame
import pygame.locals as pg
from luckypot import GFX

from ..dfont import DFont


class TextEdit:
    def __init__(
        self,
        initial_value: str,
        color,
        font: DFont,
        submit_callback: Callable[[str], None] = lambda text: None,
        autofocus: bool = False,
        font_size: int | None = None,
    ) -> None:
        """A text edit widget.

        Args:
            autofocus (bool): If True, the widget will be focused when enter is pressed.
            font_size (int | None): The font size to use. If None, the text will be as large as possible.
        """
        self.color = color
        self.font = font
        self.submit_callback = submit_callback
        self.text = initial_value
        self.editing = False
        self.autofocus = autofocus
        self.font_size = font_size

    def handle_event(self, event) -> bool:
        if not self.editing:
            if self.autofocus and event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self.editing = True
                return True
            return False

        if event.type == pg.TEXTINPUT:
            self.text += event.text
            return True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                if event.mod & pg.KMOD_CTRL:
                    self.text = re.sub(r"\S*\s*$", "", self.text)
                else:
                    self.text = self.text[:-1]
                return True
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_ESCAPE):
                self.submit_callback(self.text)
                self.editing = False
                return True
            # Paste
            elif event.key == pg.K_v and event.mod & pg.KMOD_CTRL:
                # This is a workaround for the fact that pygame doesn't handle
                # clipboard events properly on all platforms.
                try:
                    self.text += pygame.scrap.get_text()
                except Exception as e:
                    print(f"Error pasting text: {e}")
                return True
            elif event.unicode:
                # There are duplicate events for TEXTINPUT and KEYDOWN, so we
                # need to filter them out.
                return True

        return False

    def draw(self, gfx: GFX, rect: pygame.Rect):
        t = self.font.render(self.text, self.font_size or rect.size, self.color)
        r = gfx.blit(t, center=rect.center)
        if self.editing and (time() % 1) < 0.7:
            if r.height == 0:
                r.height = rect.height
            if r.right >= rect.right:
                r.right = rect.right - 3
            pygame.draw.line(gfx.surf, self.color, r.topright, r.bottomright, 2)
