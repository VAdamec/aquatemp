from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WarmLinkEntity
from .models import WarmLinkData, WarmLinkRuntimeData


@dataclass(frozen=True, kw_only=True)
class WarmLinkSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[WarmLinkData], Any]


def diagnostic_sensor(
    key: str,
    translation_key: str,
    value_fn: Callable[[WarmLinkData], Any],
) -> WarmLinkSensorEntityDescription:
    return WarmLinkSensorEntityDescription(
        key=key,
        translation_key=translation_key,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=value_fn,
    )


def diagnostic_temperature_sensor(
    key: str,
    translation_key: str,
    code: str,
) -> WarmLinkSensorEntityDescription:
    return WarmLinkSensorEntityDescription(
        key=key,
        translation_key=translation_key,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value(code),
    )


SENSOR_DESCRIPTIONS: tuple[WarmLinkSensorEntityDescription, ...] = (
    WarmLinkSensorEntityDescription(
        key="status",
        translation_key="status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status,
    ),
    WarmLinkSensorEntityDescription(
        key="fault_message",
        translation_key="fault_message",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.fault_message,
    ),
    WarmLinkSensorEntityDescription(
        key="dhw_actual_temperature",
        translation_key="dhw_actual_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("T08"),
    ),
    WarmLinkSensorEntityDescription(
        key="dhw_target_temperature",
        translation_key="dhw_target_temperature_sensor",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("R01"),
    ),
    WarmLinkSensorEntityDescription(
        key="water_inlet_temperature",
        translation_key="water_inlet_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("T02"),
    ),
    WarmLinkSensorEntityDescription(
        key="water_outlet_temperature",
        translation_key="water_outlet_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("T03"),
    ),
    WarmLinkSensorEntityDescription(
        key="ambient_temperature",
        translation_key="ambient_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("T05"),
    ),
    WarmLinkSensorEntityDescription(
        key="coil_temperature",
        translation_key="coil_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("T04"),
    ),
    WarmLinkSensorEntityDescription(
        key="suction_temperature",
        translation_key="suction_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("T01"),
    ),
    WarmLinkSensorEntityDescription(
        key="input_current",
        translation_key="input_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("InputCurrent1"),
    ),
    diagnostic_sensor(
        key="mute_timer_on_hour",
        translation_key="mute_timer_on_hour",
        value_fn=lambda data: data.value("TimerMuteOnHour"),
    ),
    diagnostic_sensor(
        key="mute_timer_on_minute",
        translation_key="mute_timer_on_minute",
        value_fn=lambda data: data.value("TimerMuteOnMinute"),
    ),
    diagnostic_sensor(
        key="mute_timer_off_enabled",
        translation_key="mute_timer_off_enabled",
        value_fn=lambda data: data.value("Timer_Mute_Off_En"),
    ),
    diagnostic_sensor(
        key="mute_timer_off_hour",
        translation_key="mute_timer_off_hour",
        value_fn=lambda data: data.value("TimerMuteOffHour"),
    ),
    diagnostic_sensor(
        key="mute_timer_off_minute",
        translation_key="mute_timer_off_minute",
        value_fn=lambda data: data.value("TimerMuteOffMinute"),
    ),
    diagnostic_sensor(
        key="compensation_slope",
        translation_key="compensation_slope",
        value_fn=lambda data: data.float_value("compensate_slope"),
    ),
    diagnostic_sensor(
        key="compensation_offset",
        translation_key="compensation_offset",
        value_fn=lambda data: data.float_value("compensate_offset"),
    ),
    diagnostic_temperature_sensor(
        key="zone_1_room_temperature",
        translation_key="zone_1_room_temperature",
        code="Zone 1 Room Temp",
    ),
    diagnostic_temperature_sensor(
        key="zone_2_room_temperature",
        translation_key="zone_2_room_temperature",
        code="Zone 2 Room Temp",
    ),
    diagnostic_temperature_sensor(
        key="zone_2_mixing_temperature",
        translation_key="zone_2_mixing_temperature",
        code="Zone 2 Mixing Temp",
    ),
    diagnostic_temperature_sensor(
        key="zone_2_water_target",
        translation_key="zone_2_water_target",
        code="Zone 2 Water Target",
    ),
    diagnostic_sensor(
        key="zone_2_curve_slope",
        translation_key="zone_2_curve_slope",
        value_fn=lambda data: data.float_value("Zone 2 Cure Slope"),
    ),
    diagnostic_sensor(
        key="zone_2_curve_offset",
        translation_key="zone_2_curve_offset",
        value_fn=lambda data: data.float_value("Zone 2 Curve Offset"),
    ),
    diagnostic_sensor(
        key="smart_grid_mode",
        translation_key="smart_grid_mode",
        value_fn=lambda data: data.value("SG01"),
    ),
    diagnostic_sensor(
        key="smart_grid_status",
        translation_key="smart_grid_status",
        value_fn=lambda data: data.value("SG Status"),
    ),
    diagnostic_sensor(
        key="fault_register_1",
        translation_key="fault_register_1",
        value_fn=lambda data: data.value("Fault1"),
    ),
    diagnostic_sensor(
        key="fault_register_5",
        translation_key="fault_register_5",
        value_fn=lambda data: data.value("Fault5"),
    ),
    diagnostic_sensor(
        key="fault_register_6",
        translation_key="fault_register_6",
        value_fn=lambda data: data.value("Fault6"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    runtime_data: WarmLinkRuntimeData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        WarmLinkSensor(runtime_data, description) for description in SENSOR_DESCRIPTIONS
    )


class WarmLinkSensor(WarmLinkEntity, SensorEntity):
    entity_description: WarmLinkSensorEntityDescription

    def __init__(
        self,
        runtime_data: WarmLinkRuntimeData,
        description: WarmLinkSensorEntityDescription,
    ) -> None:
        super().__init__(runtime_data, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        data = self.coordinator.data
        if data is None:
            return None
        return self.entity_description.value_fn(data)
