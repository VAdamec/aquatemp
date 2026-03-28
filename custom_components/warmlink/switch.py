from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WarmLinkEntity
from .models import WarmLinkRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    runtime_data: WarmLinkRuntimeData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WarmLinkSilentSwitch(runtime_data)])


class WarmLinkSilentSwitch(WarmLinkEntity, SwitchEntity):
    _attr_translation_key = "silent"

    def __init__(self, runtime_data: WarmLinkRuntimeData) -> None:
        super().__init__(runtime_data, "silent")

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if data is None:
            return None

        value = data.bool_value("Timer_Mute_On_En")
        if value is not None:
            return value

        return data.bool_value("Manual-mute")

    async def async_turn_on(self, **kwargs) -> None:
        await self.runtime_data.api.async_set_silent(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.runtime_data.api.async_set_silent(False)
        await self.coordinator.async_request_refresh()
