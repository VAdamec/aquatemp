from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AquaTempEntity
from .models import AquaTempRuntimeData

HVAC_MODE_BY_CODE = {
    "0": HVACMode.COOL,
    "1": HVACMode.HEAT,
    "2": HVACMode.AUTO,
    # Some newer devices report mode "3" while behaving like heating.
    "3": HVACMode.HEAT,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    runtime_data: AquaTempRuntimeData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AquaTempClimateEntity(runtime_data)])


class AquaTempClimateEntity(AquaTempEntity, ClimateEntity):
    _attr_translation_key = "heatpump"
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5

    def __init__(self, runtime_data: AquaTempRuntimeData) -> None:
        super().__init__(runtime_data, "climate")

    @property
    def current_temperature(self) -> float | None:
        data = self.coordinator.data
        if data is None:
            return None
        return data.float_value("T02") or data.float_value("T05")

    @property
    def target_temperature(self) -> float | None:
        data = self.coordinator.data
        if data is None:
            return None
        return data.float_value("R02")

    @property
    def min_temp(self) -> float:
        data = self.coordinator.data
        if data is None:
            return 15.0

        field = data.field("R02")
        return field.range_start if field and field.range_start is not None else 15.0

    @property
    def max_temp(self) -> float:
        data = self.coordinator.data
        if data is None:
            return 60.0

        field = data.field("R02")
        return field.range_end if field and field.range_end is not None else 60.0

    @property
    def hvac_mode(self) -> HVACMode:
        data = self.coordinator.data
        if data is None or not data.power_on:
            return HVACMode.OFF

        raw_mode = data.value("Mode")
        return HVAC_MODE_BY_CODE.get(raw_mode, HVACMode.HEAT)

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        data = self.coordinator.data
        if data is None:
            return {}

        return {
            "raw_mode_code": data.value("Mode"),
            "raw_mode_state_code": data.value("ModeState"),
        }

    async def async_set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return

        await self.runtime_data.api.async_set_target_temperature(float(kwargs[ATTR_TEMPERATURE]))
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.runtime_data.api.async_set_power(False)
        else:
            await self.runtime_data.api.async_set_mode(hvac_mode.value)

        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)
