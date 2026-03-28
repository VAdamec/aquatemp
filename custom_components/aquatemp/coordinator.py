from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AquaTempApi, AquaTempApiError, AquaTempAuthError
from .const import DOMAIN
from .models import AquaTempData

LOGGER = logging.getLogger(__name__)


class AquaTempDataUpdateCoordinator(DataUpdateCoordinator[AquaTempData]):
    def __init__(
        self,
        hass: HomeAssistant,
        api: AquaTempApi,
        update_interval_seconds: int,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
            always_update=False,
        )
        self.api = api

    async def _async_update_data(self) -> AquaTempData:
        try:
            return await self.api.async_fetch_data()
        except AquaTempAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except (AquaTempApiError, ClientError) as err:
            raise UpdateFailed(str(err)) from err
