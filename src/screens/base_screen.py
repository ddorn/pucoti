from dataclasses import dataclass
import json
from pathlib import Path

import pygame.locals as pg
import luckypot

from ..purpose import Purpose
from ..config import PucotiConfig


@dataclass
class Context:
    config: PucotiConfig
    app: luckypot.App
    history_file: Path
    purpose_history: list[Purpose]

    def __init__(self, config: PucotiConfig, app: luckypot.App):
        self.config = config
        self.app = app

        self.history_file = config.history_file.expanduser()
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.touch(exist_ok=True)

        self.purpose_history = [
            Purpose(**json.loads(line))
            for line in self.history_file.read_text().splitlines()
            if line.strip()
        ]

    def set_purpose(self, purpose: str):
        if not self.purpose_history or purpose != self.purpose_history[-1].text:
            self.purpose_history.append(Purpose(purpose))
            self.purpose_history[-1].add_to_history(self.config.history_file)


class PucotiScreen(luckypot.AppState):
    FPS = 30
    ctx: Context  # Set once the state has been pushed to the stack.

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
