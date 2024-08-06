from pathlib import Path
from time import time
from typing import Annotated
import fastapi
from pydantic import BaseModel


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

    # Delete old data (> OLD_DATA_CLEANUP seconds)
    for user, data in room_data.items():
        if time() - data.last_update > OLD_DATA_CLEANUP:
            (DATA / room_id / f"{user}.json").unlink()
            del room_data[user]

    # We sort them to avoid leaking the order of the dict, which is enough to
    # leak user ids in a room
    return sorted(room_data.values(), key=lambda x: x.username)
