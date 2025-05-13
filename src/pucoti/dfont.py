"""
This file contains utilities to render text with pygame.

The `DFont` class is a wrapper around `pygame.font.Font` that caches fonts by size and alignment
and that can wrap text, align it, respect newlines, determine the largest size of text that fits in a given space,
and draw tables.

This code is somewhat britle and unfortunately has no tests, so I don't recommend modifying it.
"""

from dataclasses import dataclass
from pathlib import Path
import re

import pygame
import pygame.locals as pg


def blit_aligned(
    surf: pygame.Surface,
    to_blit: pygame.Surface,
    y: int,
    align: int = pg.FONT_LEFT,
    left: int | None = None,
    right: int | None = None,
) -> pygame.Rect:
    if left is None:
        left = 0
    if right is None:
        right = surf.get_width()

    if align == pg.FONT_LEFT:
        return surf.blit(to_blit, (left, y))
    elif align == pg.FONT_RIGHT:
        return surf.blit(to_blit, (right - to_blit.get_width(), y))
    elif align == pg.FONT_CENTER:
        return surf.blit(to_blit, ((left + right - to_blit.get_width()) // 2, y))
    else:
        raise ValueError(f"Invalid alignment: {align}")


class DFont:
    def __init__(self, path: Path):
        self.path = path
        self.by_size: dict[tuple, pygame.Font] = {}

    def get_font(self, size: int, align: int = pg.FONT_LEFT) -> pygame.Font:
        key = size, align
        if key not in self.by_size:
            self.by_size[key] = pygame.Font(self.path, size)
            self.by_size[key].align = align
        return self.by_size[key]

    def render(
        self,
        text: str,
        size: int | tuple[int, int],
        color: tuple,
        monospaced_time: bool = False,
        align: int = pg.FONT_LEFT,
        trim_to_bounding_box: bool = True,
    ):
        if not isinstance(size, int):
            if monospaced_time:
                # Use the font size that fits a text equivalent to the time.
                # We use 0s to make sure the text is as wide as possible and doesn't jitter.
                size = self.auto_size(re.sub(r"\d", "0", text), size)
            else:
                size = self.auto_size(text, size)

        font = self.get_font(size, align)

        sizing = self.tight_size_with_newlines(text, size)

        if not monospaced_time:
            surf = font.render(text, True, color)
            if trim_to_bounding_box:
                surf = surf.subsurface(
                    (0, -sizing.y_offset, surf.get_width(), min(sizing.height, surf.get_height()))
                )
            return surf

        else:
            digits = "0123456789"
            # We render each char independently to make sure they are monospaced.
            chars = [font.render(c, True, color) for c in text]
            # Make each digit the size of a 0.
            width = font.size("0")[0]
            full_width = sum(
                s.get_width() if c not in digits else width for c, s in zip(text, chars)
            )

            # Create a surface with the correct width.
            surf = pygame.Surface((full_width, sizing.height), pg.SRCALPHA)
            # Blit each char at the correct position.
            x = 0
            for c, s in zip(text, chars):
                if c in digits:
                    blit_x = x + (width - s.get_width()) // 2
                else:
                    blit_x = x

                surf.blit(s, (blit_x, sizing.y_offset))
                x += s.get_width() if c not in digits else width

            # If \ is pressed, show the metrics of the text.
            if pygame.key.get_pressed()[pg.K_BACKSLASH]:
                pygame.draw.rect(surf, (0, 255, 0), (0, 0, surf.get_width(), surf.get_height()), 1)

            return surf

    def render_parts(
        self,
        text: list[tuple[str, pygame.Color]],
        size: int | tuple[int, int],
        align: int = pg.FONT_LEFT,
    ) -> tuple[pygame.Surface, list[pygame.Rect], int]:
        """Render a list of text parts with different colors.

        Args:
            text: A list of tuples (text, color).
            size: The font size.
            align: The alignment of the text.

        Returns:
            A tuple (surface, rects, font_size) where surface is the rendered text and rects is a list of rects for each part.
        """
        if "\n" in "".join(t[0] for t in text):
            raise ValueError("Newlines are not supported in render_parts.")

        if not isinstance(size, int):
            size = self.auto_size("".join(t[0] for t in text), size)

        font = self.get_font(size, align)
        sizing = self.tight_size_with_newlines("".join(t[0] for t in text), size)
        surf = pygame.Surface((sizing.width, sizing.height), pg.SRCALPHA)
        rects = []

        x = 0
        for part, color in text:
            part_surf = font.render(part, True, color)
            part_rect = part_surf.get_rect(topleft=(x, sizing.y_offset))
            surf.blit(part_surf, part_rect)
            rects.append(part_rect)
            x += part_rect.width

        return surf, rects, size

    @dataclass
    class TextSize:
        width: int
        height: int
        y_offset: int

    def tight_size_with_newlines(self, text: str, size: int) -> TextSize:
        """Return the size of the text with newlines and if single line, without the extra space around it."""
        lines = text.splitlines()
        font = self.get_font(size)
        line_height = font.get_height()
        if not lines:
            return self.TextSize(0, line_height, 0)
        elif len(lines) == 1:
            # If there is only one line, we can use the metrics to get the visible height,
            # with much less space around the text. This is especially relevant for Bevan.
            metrics = [m for m in font.metrics(text) if m is not None]
            min_y = min(m[2] for m in metrics)
            max_y = max(m[3] for m in metrics)
            line_height = max_y - min_y
            return self.TextSize(font.size(text)[0], line_height, -font.get_ascent() + max_y)
        else:
            return self.TextSize(
                max(font.size(line)[0] for line in lines),
                line_height * text.count("\n") + line_height,
                0,
            )

    def auto_size(self, text: str, max_rect: tuple[int, int]):
        """Find the largest font size that will fit text in max_rect."""
        # Use dichotomy to find the largest font size that will fit text in max_rect.

        min_size = 1
        max_size = max_rect[1]
        while min_size < max_size:
            font_size = (min_size + max_size) // 2
            text_size = self.tight_size_with_newlines(text, font_size)

            if text_size.width <= max_rect[0] and text_size.height <= max_rect[1]:
                min_size = font_size + 1
            else:
                max_size = font_size
        return min_size - 1

    def table(
        self,
        rows: list[list[str]],
        size: int | tuple[int, int],
        color: tuple[int, int, int] | list[tuple[int, int, int]],
        title: str | None = None,
        col_sep: str = "__",
        align: int | list[int] = pg.FONT_LEFT,
        title_color: tuple[int, int, int] | None = None,
        title_align: int = pg.FONT_CENTER,
        hidden_rows: list[list[str]] = [],
        header_line_color: tuple[int, int, int] | None = None,
    ):
        """Render a table with the given rows and size.

        Args:
            rows: The rows of the table.
            size: The font size of the table. If this is a tuple, the table is the largest that can fit in this (width, height).
            color: The text color of each column. If this is a tuple, it is used for all columns.
            title: The optional title of the table.
            col_sep: Text whose width will be used to separate columns.
            align: The alignment of each column. If this is an int, it is be used for all columns.
            title_color: The color of the title. If omitted, the color of the first column is be used.
            hidden_rows: Rows that are not rendered, but are used to size the table. Prevents change of size when scrolling.
            header_line_color: Draw a line after the first row with this color.
        """
        assert rows

        cols = list(zip(*rows, strict=True))

        if isinstance(align, int):
            align = [align] * len(cols)
        if isinstance(color, tuple):
            color = [color] * len(cols)
        assert len(align) == len(cols)
        assert len(color) == len(cols)
        if title_color is None:
            title_color = color[0]

        # It's a bit hard to size a table, we do it by creating a dummy text
        # block that has the same size.
        dummy_font = self.get_font(10)  # len() is not a good proxy for visual size.
        cols_with_hidden = list(zip(*rows, *hidden_rows, strict=True))
        longest_by_col = [max(col, key=lambda x: dummy_font.size(x)[0]) for col in cols_with_hidden]
        long_line = col_sep.join(longest_by_col)
        dummy_long_content = "\n".join([long_line] * len(rows))
        if title:
            dummy_long_content = title + "\n" + dummy_long_content

        if not isinstance(size, int):
            size = self.auto_size(dummy_long_content, size)

        font = self.get_font(size)
        surf = font.render(dummy_long_content, True, (0, 0, 0))
        surf.fill((0, 0, 0, 0))

        # Draw title
        if title:
            title_surf = font.render(title, True, title_color)
            y = blit_aligned(surf, title_surf, 0, title_align).bottom
        else:
            y = 0

        sep_width = font.size(col_sep)[0]
        column_widths = [font.size(longest)[0] for longest in longest_by_col]

        # Render each column
        x = 0
        for col, align, col_color, width in zip(cols, align, color, column_widths):
            col_surf = self.get_font(size, align).render("\n".join(col), True, col_color)
            blit_aligned(surf, col_surf, y, align, x, x + width)
            x += width + sep_width

        # Draw a line under the header
        if header_line_color is not None:
            y += font.get_height()
            pygame.draw.line(surf, header_line_color, (0, y), (surf.get_width(), y), 1)

        return surf
