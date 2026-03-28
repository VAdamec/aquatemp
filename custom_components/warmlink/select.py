from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WarmLinkEntity
from .models import WarmLinkRuntimeData

OPTION_BY_CODE = {
    "1": "water",
    "2": "heat",
    "3": "dhw",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    runtime_data: WarmLinkRuntimeData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WarmLinkOperatingModeSelect(runtime_data)])


class WarmLinkOperatingModeSelect(WarmLinkEntity, SelectEntity):
    _attr_translation_key = "operating_mode"
    _attr_options = ["water", "heat", "dhw"]

    def __init__(self, runtime_data: WarmLinkRuntimeData) -> None:
        super().__init__(runtime_data, "operating_mode")

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data
        if data is None:
            return None
        return OPTION_BY_CODE.get(data.value("Mode"))

    async def async_select_option(self, option: str) -> None:
        await self.runtime_data.api.async_set_mode(option)
        await self.coordinator.async_request_refresh()
