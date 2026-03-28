from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from aiohttp import ClientError

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import WarmLinkApi, WarmLinkApiError, WarmLinkAuthError
from .const import (
    CONF_DEVICE_CODE,
    CONF_DEVICE_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)
from .models import WarmLinkDevice

LOGGER = logging.getLogger(__name__)


class WarmLinkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._pending_input: dict[str, Any] = {}
        self._devices: list[WarmLinkDevice] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            api = WarmLinkApi(
                async_get_clientsession(self.hass),
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )

            try:
                self._devices = await api.async_get_devices()
            except WarmLinkAuthError:
                errors["base"] = "invalid_auth"
            except (WarmLinkApiError, ClientError):
                LOGGER.exception("Unable to connect to WarmLink")
                errors["base"] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected error while validating WarmLink credentials")
                errors["base"] = "unknown"
            else:
                if not self._devices:
                    errors["base"] = "no_devices"
                else:
                    self._pending_input = {
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    }

                    if len(self._devices) == 1:
                        return await self._async_create_entry_for_device(self._devices[0])

                    return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
            errors=errors,
        )

    async def async_step_device(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_code = user_input[CONF_DEVICE_CODE]
            for device in self._devices:
                if device.code == selected_code:
                    return await self._async_create_entry_for_device(device)

            errors["base"] = "unknown"

        options = {device.code: _device_label(device) for device in self._devices}
        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_CODE): vol.In(options),
                }
            ),
            errors=errors,
        )

    async def _async_create_entry_for_device(self, device: WarmLinkDevice):
        await self.async_set_unique_id(device.code)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=_device_label(device),
            data={
                **self._pending_input,
                CONF_DEVICE_CODE: device.code,
                CONF_DEVICE_NAME: device.name,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return WarmLinkOptionsFlowHandler(config_entry)


class WarmLinkOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
        )


def _device_label(device: WarmLinkDevice) -> str:
    if device.model:
        return f"{device.name} ({device.model})"
    return device.name
