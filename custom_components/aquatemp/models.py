from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .api import AquaTempApi
    from .coordinator import AquaTempDataUpdateCoordinator


@dataclass(slots=True, frozen=True)
class AquaTempDevice:
    code: str
    name: str
    model: str | None = None
    serial_number: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AquaTempField:
    value: str | None = None
    range_start: float | None = None
    range_end: float | None = None


@dataclass(slots=True, frozen=True)
class AquaTempData:
    device: AquaTempDevice
    status: str
    is_fault: bool
    fault_message: str
    fields: dict[str, AquaTempField]

    @property
    def online(self) -> bool:
        return self.status.upper() == "ONLINE"

    @property
    def power_on(self) -> bool:
        return self.value("Power") == "1"

    def field(self, code: str) -> AquaTempField | None:
        return self.fields.get(code)

    def value(self, code: str) -> str | None:
        field = self.field(code)
        if field is None:
            return None
        return field.value

    def float_value(self, code: str) -> float | None:
        value = self.value(code)
        if value in (None, ""):
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def bool_value(self, code: str) -> bool | None:
        value = self.value(code)
        if value is None:
            return None
        return value in {"1", "true", "TRUE", "on", "ON"}


@dataclass(slots=True)
class AquaTempRuntimeData:
    api: AquaTempApi
    coordinator: AquaTempDataUpdateCoordinator
