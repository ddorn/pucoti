from importlib.metadata import PackageNotFoundError, version
from typing import Mapping
import os
import platform
import threading

import umami

from . import constants


class TelemetryClient:
    def __init__(self, telemetry_enabled: bool):
        self.enabled = telemetry_enabled
        self.client_id = constants.USER_ID
        self._version = self._resolve_version()

        umami.set_url_base(constants.UMAMI_URL_BASE)
        umami.set_website_id(constants.UMAMI_WEBSITE_ID)
        umami.set_hostname(constants.UMAMI_HOSTNAME)

    def emit_app_started(self) -> None:
        data = self._base_payload()
        data.update(self._environment_payload())
        self._emit("app_started", data)

    def emit_social_join(self) -> None:
        payload = self._base_payload()
        self._emit("social_join", payload)

    def _emit(self, event_name: str, data: Mapping[str, str]) -> None:
        if not self.enabled:
            return

        custom_data = dict(data)
        custom_data["client_id"] = self.client_id

        def new_event():
            try:
                umami.new_event(
                    event_name=event_name,
                    custom_data=custom_data,
                    url="/pucoti",
                )
            except Exception as exc:
                print(f"Telemetry send failed: {exc}")

        threading.Thread(target=new_event).start()

    def _environment_payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}

        system = platform.system()
        if system:
            payload["platform"] = system

        release = platform.release()
        if release:
            payload["platform_release"] = release

        desktop = os.environ.get("XDG_CURRENT_DESKTOP")
        if desktop:
            payload["XDG_CURRENT_DESKTOP"] = desktop

        session = os.environ.get("DESKTOP_SESSION")
        if session:
            payload["DESKTOP_SESSION"] = session

        wm = os.environ.get("XDG_SESSION_DESKTOP")
        if wm:
            payload["XDG_SESSION_DESKTOP"] = wm

        return payload

    def _base_payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}
        if self._version:
            payload["version"] = self._version
        return payload

    def _resolve_version(self) -> str:
        try:
            return version("pucoti")
        except PackageNotFoundError:
            return "dev"
