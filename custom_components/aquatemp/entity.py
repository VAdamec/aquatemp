from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import AquaTempDataUpdateCoordinator
from .models import AquaTempRuntimeData


class AquaTempEntity(CoordinatorEntity[AquaTempDataUpdateCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, runtime_data: AquaTempRuntimeData, unique_suffix: str) -> None:
        super().__init__(runtime_data.coordinator)
        self.runtime_data = runtime_data
        device_code = runtime_data.api.device_code or "unknown"
        self._attr_unique_id = f"{device_code}_{unique_suffix}"

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.online
        )

    @property
    def device_info(self) -> DeviceInfo:
        data = self.coordinator.data
        device_code = self.runtime_data.api.device_code or "unknown"
        name = data.device.name if data else device_code
        model = data.device.model if data else None
        serial_number = data.device.serial_number if data else None
        sw_version = data.value("code_version") if data else None
        hw_version = data.value("MainBoard Version") if data else None

        return DeviceInfo(
            identifiers={(DOMAIN, device_code)},
            manufacturer=MANUFACTURER,
            name=name,
            model=model,
            serial_number=serial_number,
            sw_version=sw_version,
            hw_version=hw_version,
        )
