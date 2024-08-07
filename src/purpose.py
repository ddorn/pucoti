from dataclasses import dataclass
import dataclasses
import json
from time import time
from pathlib import Path


@dataclass
class Purpose:
    text: str
    timestamp: float = dataclasses.field(default_factory=time)

    def add_to_history(self, history_file: Path):
        with history_file.expanduser().open("a") as f:
            f.write(json.dumps(self.__dict__) + "\n")
