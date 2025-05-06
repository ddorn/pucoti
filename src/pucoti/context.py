import json
import threading
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import TYPE_CHECKING

import luckypot
import pygame

from .callback import CountdownCallback

from . import constants, db, time_utils, pygame_utils
from .config import PucotiConfig
from .purpose import Purpose
from .server_comunication import UpdateRoomRequest, UserData, send_update

if TYPE_CHECKING:
    from .app import App


@dataclass
class Context:
    config: PucotiConfig
    app: "App"
    history_file: Path
    purpose_history: list[Purpose]
    friend_activity: list[UserData]

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

        self.initial_duration = time_utils.human_duration(self.config.initial_timer)
        self.start = round(time())
        self.timer_end = 0.0
        """Timestamp when the timer hits 0."""
        self.last_rung = 0.0
        self.nb_rings = 0

        self.callbacks = [CountdownCallback(cfg) for cfg in self.config.run_at]

        self.friend_activity = []
        self.last_server_update = 0.0

        self.set_timer_to(self.initial_duration)
        self.set_purpose("", force=True)

    @property
    def remaining_time(self) -> float:
        return self.timer_end - (time() - self.start)

    @property
    def purpose(self) -> str:
        return self.purpose_history[-1].text

    @property
    def purpose_start_time(self):
        return round(self.purpose_history[-1].timestamp)

    def set_purpose(self, purpose: str, force: bool = False):
        if force or not self.purpose_history or purpose != self.purpose_history[-1].text:
            self.purpose_history.append(Purpose(purpose))
            self.purpose_history[-1].add_to_history(self.config.history_file)
            db.store(db.Action.purpose(purpose))

            if purpose:
                pygame.display.set_caption(f"PUCOTI - {purpose}")
            else:
                pygame.display.set_caption("PUCOTI")

            self.update_servers(force=True)

    def set_timer_to(self, new_duration: float):
        self.timer_end = time_utils.compute_timer_end(new_duration, self.start)
        db.store(db.Action.set_timer(timer=new_duration))

    def shift_timer(self, delta: float):
        self.timer_end += delta
        db.store(db.Action.set_timer(timer=self.remaining_time))

    def update_servers(self, force: bool = False):
        next_update = self.last_server_update + constants.UPDATE_SERVER_EVERY
        if not force and time() < next_update:
            return

        self.last_server_update = time()

        social = self.config.social
        payload = UpdateRoomRequest(
            username=social.username,
            timer_end=self.timer_end,
            start=self.start,
            purpose=self.purpose if social.send_purpose else None,
            purpose_start=self.purpose_start_time if social.send_purpose else None,
        )

        if social.enabled:

            def send_update_thread():
                data = send_update(social.server, social.room, constants.USER_ID, payload)
                self.friend_activity = data

            threading.Thread(target=send_update_thread).start()

    def ring_if_needed(self):
        remaining = self.remaining_time
        if (
            remaining < 0
            and time() - self.last_rung > self.config.ring_every
            and self.nb_rings != self.config.ring_count
        ):
            self.last_rung = time()
            self.nb_rings += 1
            pygame_utils.play(self.config.bell)
            if self.config.restart:
                # self.timer_end = self.initial_duration + (round(time() + 0.5) - self.start)
                self.timer_end = time_utils.compute_timer_end(self.initial_duration, self.start)

        elif remaining > 0:
            self.nb_rings = 0
            self.last_rung = 0

        # And execute the callbacks.
        for callback in self.callbacks:
            callback.update(self.timer_end - (time() - self.start))
