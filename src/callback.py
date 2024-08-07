import subprocess

from src import time_utils
from src.config import RunAtConfig


class CountdownCallback:
    """Call a command once the timer goes below a specific time."""

    def __init__(self, cfg: RunAtConfig) -> None:
        self.command = cfg.cmd
        self.time = time_utils.human_duration(cfg.at)
        self.executed = False

    def update(self, current_time: float):
        """Call the command if needed. Current time is the number of seconds on screen."""
        if current_time >= self.time:
            self.executed = False
        elif not self.executed:
            self.executed = True
            # Asynchronously run the command.
            print(f"Running: {self.command}")
            subprocess.Popen(self.command, shell=True)
