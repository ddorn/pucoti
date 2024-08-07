from pathlib import Path
from time import time
from typing import Annotated
import fastapi
from pydantic import BaseModel
import requests


DATA = Path(__file__).parent.parent / "data"
DATA.mkdir(exist_ok=True)

OLD_DATA_CLEANUP = 5 * 60  # 5 minutes

app = fastapi.FastAPI()


class UpdateRoomRequest(BaseModel):
    username: str
    timer_end: float
    start: float
    purpose: str | None = None
    purpose_start: float | None = None


class UserData(UpdateRoomRequest):
    last_update: float


def delete_old_data(folder: Path, max_age_seconds: int):
    """Delete all files, recursively in folder, older than max_age_seconds."""

    for file in folder.iterdir():
        if file.is_dir():
            delete_old_data(file, max_age_seconds)
            if not any(file.iterdir()):
                file.rmdir()
        elif time() - file.stat().st_mtime > max_age_seconds:
            file.unlink()


@app.put("/room/{room_id}/user/{user_id}", response_model=list[UserData])
async def update(
    room_id: Annotated[
        str, fastapi.Path(min_length=1, max_length=30, pattern=r"^[a-zA-Z0-9_+ -]+$")
    ],
    user_id: Annotated[
        str, fastapi.Path(min_length=1, max_length=30, pattern=r"^[a-zA-Z0-9_+ -]+$")
    ],
    request: UpdateRoomRequest,
):
    # Delete old data (> OLD_DATA_CLEANUP seconds)
    delete_old_data(DATA, OLD_DATA_CLEANUP)

    file = DATA / room_id / f"{user_id}.json"
    file.parent.mkdir(exist_ok=True)
    data = UserData(
        **request.model_dump(),
        last_update=time(),
    )
    file.write_text(data.model_dump_json())

    # Read data from all users in the room
    room_data = {}
    for user_file in (DATA / room_id).iterdir():
        user = user_file.stem
        room_data[user] = UserData.model_validate_json(user_file.read_text())

    # We sort them to avoid leaking the order of the dict, which is enough to
    # leak user ids in a room
    return sorted(room_data.values(), key=lambda x: x.username)


def send_update(server_url: str, room_id: str, user_id: str, data: UpdateRoomRequest):
    requests.put(f"{server_url}/room/{room_id}/user/{user_id}", json=data.model_dump())
