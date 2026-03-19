"""DataUpdateCoordinator for EAC."""
import logging
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL
from .eac import EACClient



_LOGGER: logging.Logger = logging.getLogger(__package__)


class EACUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data"""

    def __init__( self, hass: HomeAssistant, email, password ) -> None:
        """Initialize."""

        self._email = email
        self._password = password
        self._hass = hass

        super().__init__(
            hass=hass, logger=_LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL
        )
        self._eac_client = EACClient(email, password)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data """
        try:
            rez = {}
            # #both data, same dictionary under different keys
            # _LOGGER.debug("Get the latest data from cyprus-weather.org for %s ", self._city)
            # newWeatherData = await self._hass.async_add_executor_job(get_weather_data,self._city)
            # rez[WEATHER_KEY] = newWeatherData

            # _LOGGER.debug("Get the latest data from www.airquality.dli.mlsi.gov.cy for %s ", self._city)
            # newAirQualityData = await self._hass.async_add_executor_job(get_air_quality_data,self._city)
            # rez[AIR_QUALITY_KEY] = newAirQualityData

            return rez
        except Exception as exception:
            _LOGGER.error("Update failed! - %s", exception)
            raise UpdateFailed() from exception

    # def get_weather_value( self, key: str ) -> float | int | str | None:
    #     if self.data and WEATHER_KEY in self.data and key in self.data[WEATHER_KEY]:
    #         return self.data[WEATHER_KEY].get(key, None)

    #     _LOGGER.debug("Value %s is missing in API response", key)
    #     return None
    
    # def get_air_quality_value( self, key: str ) -> float | int | str | None:
    #     if self.data and AIR_QUALITY_KEY in self.data and key in self.data[AIR_QUALITY_KEY]:
    #         return self.data[AIR_QUALITY_KEY].get(key, None)

    #     _LOGGER.debug("Value %s is missing in API response", key)
    #     return None    