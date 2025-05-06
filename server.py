from pathlib import Path
from time import time
from typing import Annotated
from typing import Callable
import threading

import requests
from pydantic import BaseModel
import fastapi
from fastapi.staticfiles import StaticFiles


DATA = Path(__file__).parent.parent / "data"

OLD_DATA_CLEANUP = 1 * 60  # 1 minute

app = fastapi.FastAPI()


class UpdateRoomRequest(BaseModel):
    username: str
    timer_end: float
    start: float
    purpose: str | None = None
    purpose_start: float | None = None


class UserData(UpdateRoomRequest):
    last_update: float


def send_update(
    server_url: str, room_id: str, user_id: str, data: UpdateRoomRequest
) -> list[UserData]:
    response = requests.put(f"{server_url}/room/{room_id}/user/{user_id}", json=data.model_dump())
    if response.status_code != 200:
        try:
            print(response.json())
        except Exception:
            print(response.text)
        return []
    return [UserData.model_validate(user_data) for user_data in response.json()]


def send_update_thread(
    server_url: str,
    room_id: str,
    user_id: str,
    data: UpdateRoomRequest,
    callback: Callable[[list[UserData]], None],
) -> None:

    def send_update_thread_inner():
        friends = send_update(server_url, room_id, user_id, data)
        callback(friends)

    threading.Thread(target=send_update_thread_inner).start()


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


# Serve the frontend (/build) at the root
app.mount("/", StaticFiles(directory=Path(__file__).parent / "dist", html=True))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
