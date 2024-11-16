from pathlib import Path
from time import time
from typing import Annotated

import fastapi

from .server_comunication import UpdateRoomRequest, UserData


DATA = Path(__file__).parent.parent / "data"

OLD_DATA_CLEANUP = 1 * 60  # 1 minute

app = fastapi.FastAPI()


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
        str, fastapi.Path(min_length=1, max_length=40, pattern=r"^[a-zA-Z0-9_+ -]+$")
    ],
    user_id: Annotated[
        str, fastapi.Path(min_length=1, max_length=40, pattern=r"^[a-zA-Z0-9_+ -]+$")
    ],
    request: UpdateRoomRequest,
):
    DATA.mkdir(exist_ok=True)
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
