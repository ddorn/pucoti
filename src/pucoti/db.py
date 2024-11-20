from __future__ import annotations

from .constants import DATA_DIR

# %%
from typing import ClassVar, Iterator, Literal
import time
from pathlib import Path
from pydantic import BaseModel

# %%


class PucotiModel(BaseModel):
    # Table is not part of the pydantic model, it's just where we store the data

    table: ClassVar[str | None] = None

    @classmethod
    def get_filename(cls):
        cls.model_config
        if cls.table is None:
            raise ValueError(f"table is not defined for {cls}. Cannot get filename.")
        return cls.table + ".jsonl"


class FocusedWindow(PucotiModel):
    start: float
    end: float
    window_title: str
    window_class: str

    table: ClassVar[str] = "focused_windows"


class SetPurposeArgs(PucotiModel):
    purpose: str
    action: Literal["set_purpose"] = "set_purpose"


class SetTimerArgs(PucotiModel):
    timer: float
    action: Literal["set_time"] = "set_time"


class Action(PucotiModel):
    table: ClassVar[str] = "actions"

    time: float
    content: SetPurposeArgs | SetTimerArgs

    @classmethod
    def purpose(cls, purpose: str) -> Action:
        return cls(time=time.time(), content=SetPurposeArgs(purpose=purpose))

    @classmethod
    def set_timer(cls, timer: float) -> Action:
        return cls(time=time.time(), content=SetTimerArgs(timer=timer))


def store(data: PucotiModel):
    """Store data in the database."""

    table = data.get_filename()
    now = time.time()
    # Note: This does not take the timezone into account.
    # Indeed, I want things to represent the current day for people
    # BUT it means that there might be overlaps when people switch timezones.
    date = time.strftime("%Y/%m/%d/%H", time.localtime(now))
    path = Path(DATA_DIR) / date / table
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a") as f:
        f.write(data.model_dump_json() + "\n")


def sorted_walk_dirs(path: Path, contains: str):
    """Walk through a directory, yielding sorted folders that contain a given filename."""
    for folder in sorted(path.iterdir()):
        if folder.is_dir():
            if (folder / contains).exists():
                yield folder
            yield from sorted_walk_dirs(folder, contains)


def load_all[T: PucotiModel](type_: type[T]) -> Iterator[T]:
    """Load all entries of a given type."""
    table = type_.get_filename()

    # For all folders, sorted by date
    for folder in sorted_walk_dirs(Path(DATA_DIR), table):
        path = folder / table
        yield from load_all_file(path, type_)


def load_all_file[T: PucotiModel](path: Path, type_: type[T]) -> Iterator[T]:
    """Load all entries of a given type from a file."""
    with path.open("r") as f:
        for line in f:
            yield type_.model_validate_json(line, strict=False)
