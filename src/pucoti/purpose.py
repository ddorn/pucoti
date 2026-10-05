import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from time import time


@dataclass
class Purpose:
    text: str
    timestamp: float = dataclasses.field(default_factory=time)

    def add_to_history(self, history_file: Path):
        with history_file.expanduser().open("a") as f:
            f.write(json.dumps(self.__dict__) + "\n")
