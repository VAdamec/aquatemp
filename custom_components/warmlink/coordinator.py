from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WarmLinkApi, WarmLinkApiError, WarmLinkAuthError
from .const import DOMAIN
from .models import WarmLinkData

LOGGER = logging.getLogger(__name__)


class WarmLinkDataUpdateCoordinator(DataUpdateCoordinator[WarmLinkData]):
    def __init__(
        self,
        hass: HomeAssistant,
        api: WarmLinkApi,
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

    async def _async_update_data(self) -> WarmLinkData:
        try:
            return await self.api.async_fetch_data()
        except WarmLinkAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except (WarmLinkApiError, ClientError) as err:
            raise UpdateFailed(str(err)) from err
