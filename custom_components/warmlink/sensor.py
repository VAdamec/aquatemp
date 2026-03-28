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
        key="dhw_temperature",
        translation_key="dhw_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.float_value("T08"),
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
