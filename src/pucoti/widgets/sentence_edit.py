from dataclasses import dataclass
from time import time
from typing import Callable

import pygame
import pygame.locals as pg
from luckypot import GFX

from ..dfont import DFont
from .text_edit import TextEdit


__all__ = ["SentenceEdit", "Field"]


@dataclass
class Field:
    name: str
    initial_value: str
    color: tuple[int, int, int]


class SentenceEdit:
    def __init__(
        self,
        parts: list[str | Field],
        text_color,
        font: DFont,
        submit_callback: Callable[[dict[str, str]], None] = lambda data: None,
        help_text: str = "CTRL+ENTER to submit",
    ) -> None:
        """A widget to edit a sentence with multiple fields."""
        self.parts = parts
        self.text_color = text_color
        self.font = font
        self.submit_callback = submit_callback
        self.editing: int = 0
        self.help_text = help_text

        self.fields = [f for f in parts if isinstance(f, Field)]

        if len(self.fields) == 0:
            raise ValueError("At least one field is required")
        if len(self.fields) != len(set(f.name for f in self.fields)):
            raise ValueError(f"Field names must be unique, got {[f.name for f in self.fields]}")

        self.text_edits = {
            f.name: TextEdit(
                f.initial_value,
                f.color,
                font,
                lambda text, name=f.name: self.field_callback(name, text),
            )
            for f in self.fields
        }
        self.edit_next(0)

    def field_callback(self, name: str, text: str):
        self.edit_next(1)

    def handle_event(self, event) -> bool:
        if self.editing is None:
            return False

        # Switch to the next/previous field
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB:
                if event.mod & pg.KMOD_SHIFT:
                    self.edit_next(-1)
                else:
                    self.edit_next(1)

                return True

            elif event.key == pg.K_RETURN:
                if event.mod & pg.KMOD_CTRL:
                    self.submit_callback(
                        {f.name: self.text_edits[f.name].text for f in self.fields}
                    )
                    return True
                self.edit_next(1)
                return True

        return self.text_edits[self.fields[self.editing].name].handle_event(event)

    def edit_next(self, diff: int):
        self.text_edits[self.fields[self.editing].name].editing = False
        self.editing = (self.editing + diff) % len(self.fields)
        self.text_edits[self.fields[self.editing].name].editing = True

    def draw(self, gfx: GFX, rect: pygame.Rect):
        parts = [
            (f, self.text_color) if isinstance(f, str) else (self.text_edits[f.name].text, f.color)
            for f in self.parts
        ]
        text, rects, font_size = self.font.render_parts(parts, rect.size, align=pygame.FONT_CENTER)

        sentence_r = gfx.blit(text, center=rect.center)
        for r in rects:
            r.move_ip(sentence_r.topleft)

        for part, field_r in zip(self.parts, rects):
            if isinstance(part, Field):
                text_edit = self.text_edits[part.name]
                if text_edit.editing and (time() % 1) < 0.7:
                    gfx.line(part.color, field_r.topright, field_r.bottomright)

        if self.help_text:
            gfx.blit(
                self.font.render(self.help_text, font_size // 3, self.text_color),
                topright=rects[-1].bottomright,
            )
