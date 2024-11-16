from typing import Callable
import threading

import requests
from pydantic import BaseModel


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
