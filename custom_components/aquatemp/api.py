from __future__ import annotations

import hashlib
import re
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import APP_ID, CLOUD_URL, LANGUAGE, REQUEST_CODES
from .models import AquaTempData, AquaTempDevice, AquaTempField

MD5_RE = re.compile(r"^[0-9a-fA-F]{32}$")


class AquaTempApiError(Exception):
    """Raised when the AquaTemp API returns an error."""


class AquaTempAuthError(AquaTempApiError):
    """Raised when authentication fails."""


class AquaTempApi:
    def __init__(
        self,
        session: ClientSession,
        username: str,
        password: str,
        device_code: str | None = None,
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._password_hash = self._hash_password(password)
        self._device_code = device_code
        self._token: str | None = None
        self._device: AquaTempDevice | None = None

    @property
    def device(self) -> AquaTempDevice | None:
        return self._device

    @property
    def device_code(self) -> str | None:
        return self._device_code

    def _hash_password(self, raw_password: str) -> str:
        if MD5_RE.match(raw_password):
            return raw_password.lower()

        return hashlib.md5(raw_password.encode("utf-8"), usedforsecurity=False).hexdigest()

    def _app_url(self, endpoint: str) -> str:
        return f"{CLOUD_URL}/app/{endpoint}?lang={LANGUAGE}"

    async def _async_post(
        self,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        headers = {"Content-Type": "application/json; charset=utf-8"}

        if token:
            headers["x-token"] = token

        try:
            response = await self._session.post(
                self._app_url(endpoint),
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
        except (ClientError, ClientResponseError) as err:
            raise AquaTempApiError(f"HTTP error calling {endpoint}: {err}") from err

        try:
            return await response.json(content_type=None)
        except Exception as err:
            raise AquaTempApiError(f"Invalid JSON returned by {endpoint}") from err

    def _raise_for_response_error(self, response: dict[str, Any]) -> None:
        error_code = str(response.get("error_code", "0"))
        if error_code in {"0", "", "None"}:
            return

        message = response.get("error_msg") or f"AquaTemp API error {error_code}"
        if error_code == "-100":
            raise AquaTempAuthError(message)

        raise AquaTempApiError(message)

    async def _async_login(self) -> None:
        payload = {
            "password": self._password_hash,
            "loginSource": "IOS",
            "areaCode": "en",
            "appId": APP_ID,
            "type": "2",
            "userName": self._username,
        }
        response = await self._async_post("user/login", payload)
        self._raise_for_response_error(response)

        token = response.get("objectResult", {}).get("x-token")
        if not token:
            raise AquaTempAuthError("Login succeeded but no token was returned")

        self._token = token

    async def _async_request(
        self,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self._token is None:
            await self._async_login()

        try:
            response = await self._async_post(endpoint, payload, self._token)
            self._raise_for_response_error(response)
            return response
        except AquaTempAuthError:
            await self._async_login()
            response = await self._async_post(endpoint, payload, self._token)
            self._raise_for_response_error(response)
            return response

    def _parse_devices(self, response: dict[str, Any]) -> list[AquaTempDevice]:
        devices: list[AquaTempDevice] = []

        for raw_device in response.get("objectResult") or []:
            code = raw_device.get("deviceCode") or raw_device.get("device_code")
            if not code:
                continue

            name = (
                raw_device.get("deviceNickName")
                or raw_device.get("device_nick_name")
                or raw_device.get("deviceName")
                or raw_device.get("device_name")
                or code
            )
            devices.append(
                AquaTempDevice(
                    code=code,
                    name=name,
                    model=raw_device.get("custModel") or raw_device.get("model"),
                    serial_number=raw_device.get("sn"),
                    raw=raw_device,
                )
            )

        return devices

    async def async_get_devices(self) -> list[AquaTempDevice]:
        response = await self._async_request("device/deviceList")
        return self._parse_devices(response)

    async def _async_ensure_device(self) -> AquaTempDevice:
        devices = await self.async_get_devices()

        if not devices:
            raise AquaTempApiError("No AquaTemp devices were found on this account")

        if self._device_code is None:
            self._device = devices[0]
            self._device_code = devices[0].code
            return devices[0]

        for device in devices:
            if device.code == self._device_code:
                self._device = device
                return device

        raise AquaTempApiError(f"Configured device {self._device_code} was not found")

    async def async_fetch_data(self) -> AquaTempData:
        device = await self._async_ensure_device()
        payload = {"deviceCode": device.code}
        status_response = await self._async_request("device/getDeviceStatus", payload)

        info_response = await self._async_request(
            "device/getDataByCode",
            {
                "deviceCode": device.code,
                "appId": APP_ID,
                "protocalCodes": list(REQUEST_CODES),
            },
        )

        status_payload = status_response.get("objectResult") or {}
        is_fault = bool(status_payload.get("is_fault", status_payload.get("isFault", False)))
        fault_message = "No error"

        if is_fault:
            try:
                fault_response = await self._async_request(
                    "device/getFaultDataByDeviceCode",
                    payload,
                )
            except AquaTempApiError:
                fault_message = "Fault details unavailable"
            else:
                descriptions = [
                    item.get("description")
                    for item in (fault_response.get("objectResult") or [])
                    if item.get("description")
                ]
                fault_message = descriptions[0] if descriptions else "Fault details unavailable"

        fields: dict[str, AquaTempField] = {}
        for item in info_response.get("objectResult") or []:
            code = item.get("code")
            if not code:
                continue

            fields[code] = AquaTempField(
                value=item.get("value"),
                range_start=_parse_float(item.get("rangeStart")),
                range_end=_parse_float(item.get("rangeEnd")),
            )

        return AquaTempData(
            device=device,
            status=str(status_payload.get("status", "UNKNOWN")),
            is_fault=is_fault,
            fault_message=fault_message,
            fields=fields,
        )

    async def _async_control(self, protocol_code: str, value: str) -> None:
        device = await self._async_ensure_device()
        payload = {
            "param": [
                {
                    "deviceCode": device.code,
                    "protocolCode": protocol_code,
                    "value": value,
                }
            ]
        }
        await self._async_request("device/control", payload)

    async def async_set_power(self, enabled: bool) -> None:
        await self._async_control("Power", "1" if enabled else "0")

    async def async_set_mode(self, mode: str) -> None:
        mode_map = {
            "cool": "0",
            "heat": "1",
            "auto": "2",
        }
        if mode not in mode_map:
            raise AquaTempApiError(f"Unsupported mode: {mode}")

        await self.async_set_power(True)
        await self._async_control("Mode", mode_map[mode])

    async def async_set_target_temperature(self, temperature: float) -> None:
        await self._async_control("R02", f"{temperature:.1f}".rstrip("0").rstrip("."))

    async def async_set_dhw_temperature(self, temperature: float) -> None:
        await self._async_control("R01", f"{temperature:.1f}".rstrip("0").rstrip("."))

    async def async_set_silent(self, enabled: bool) -> None:
        await self._async_control("Timer_Mute_On_En", "1" if enabled else "0")


def _parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None
