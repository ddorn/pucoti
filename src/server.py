from pathlib import Path
from time import time
import fastapi
from pydantic import BaseModel


DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)


app = fastapi.FastAPI()


class UpdateRoomRequest(BaseModel):
    user: str
    timer_end: float
    start: float
    purpose: str | None = None
    purpose_start: float | None = None


class UpdateRoomData(UpdateRoomRequest):
    last_update: float


@app.put("/room/{room_id}")
async def update(
    room_id: str,
    request: UpdateRoomRequest,
):
    file = DATA / room_id / f"{request.user}.json"
    file.parent.mkdir(exist_ok=True)
    data = UpdateRoomData(
        **request.model_dump(),
        last_update=time(),
    )
    file.write_text(data.model_dump_json())

    # Read data from all users in the room
    room_data = {}
    for user_file in (DATA / room_id).iterdir():
        user = user_file.stem
        room_data[user] = UpdateRoomData.model_validate_json(user_file.read_text())

    # Delete old data (> 5 minutes)
    for user, data in room_data.items():
        if time() - data.last_update > 5 * 60:
            (DATA / room_id / f"{user}.json").unlink()
            del room_data[user]

    return room_data
