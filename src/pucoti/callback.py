import traceback
import subprocess

from . import time_utils
from .config import RunAtConfig


class CountdownCallback:
    """Call a command once the timer goes below a specific time."""

    def __init__(self, cfg: RunAtConfig) -> None:
        self.command = cfg.cmd
        self.cmd_type = cfg.cmd_type
        self.time = time_utils.human_duration(cfg.at)
        self.every: float | None = time_utils.human_duration(cfg.every) if cfg.every else None
        self.last_executed: float | None = None

        # self.executed = False

    def update(self, current_time: float):
        """Call the command if needed. Current time is the number of seconds on screen."""
        if current_time >= self.time:
            self.last_executed = None
        elif self.last_executed is None:
            self.last_executed = current_time
            self.run()
        elif self.every is not None and self.last_executed - current_time >= self.every:
            self.last_executed = current_time
            self.run()

    def run(self):
        """Asynchronously run the command."""
        try:
            if self.cmd_type == "shell":
                subprocess.Popen(self.command, shell=True)
            elif self.cmd_type == "python":
                exec(self.command)
        except Exception:
            print(f"Failed to run command {self.command}")
            traceback.print_exc()
