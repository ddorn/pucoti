import subprocess

from src import time_utils


class CountdownCallback:
    """Call a command once the timer goes below a specific time."""

    def __init__(self, time_and_command: str) -> None:
        time, _, command = time_and_command.partition(":")
        self.command = command
        if isinstance(time, str):
            self.time = time_utils.human_duration(time)
        else:
            self.time = time
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
