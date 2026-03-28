from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AquaTempEntity
from .models import AquaTempRuntimeData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    runtime_data: AquaTempRuntimeData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AquaTempDhwTargetTemperatureNumber(runtime_data)])


class AquaTempDhwTargetTemperatureNumber(AquaTempEntity, NumberEntity):
    _attr_translation_key = "dhw_target_temperature"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_step = 0.5

    def __init__(self, runtime_data: AquaTempRuntimeData) -> None:
        super().__init__(runtime_data, "dhw_target_temperature")

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if data is None:
            return None
        return data.float_value("R01")

    @property
    def native_min_value(self) -> float:
        data = self.coordinator.data
        if data is None:
            return 15.0

        field = data.field("R01")
        return field.range_start if field and field.range_start is not None else 15.0

    @property
    def native_max_value(self) -> float:
        data = self.coordinator.data
        if data is None:
            return 48.0

        field = data.field("R01")
        return field.range_end if field and field.range_end is not None else 48.0

    async def async_set_native_value(self, value: float) -> None:
        await self.runtime_data.api.async_set_dhw_temperature(value)
        await self.coordinator.async_request_refresh()
