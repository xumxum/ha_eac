"""Platform for sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from homeassistant.const import UnitOfEnergy

from .const import DEFAULT_NAME, DOMAIN
#from .coordinator import CyprusWeatherUpdateCoordinator
#from .air_quality import get_air_quality_parameters

_LOGGER = logging.getLogger(__name__)


eac_sensors: list[SensorEntityDescription] = [
    SensorEntityDescription(
        key="Consumption",
        name="Consumption",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Production",
        name="Production",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
    )
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EAC sensors based on a config entry."""
    #coordinator = hass.data[DOMAIN][entry.entry_id]
    #city = entry.data.get(CONF_CITY)

    entities= []

    # Add all meter sensors described above.
    for eac_sensor in eac_sensors:
        entities.append(
            EACSensor(
                entry=entry,
                description=eac_sensor,
            )
        )

    async_add_entities(entities)




class EACSensor(SensorEntity):
    """Defines a EACSensor ."""

    #_attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        description: SensorEntityDescription
    ) -> None:
        
        """Initialize EACSensor."""
        self._name = description.name
        self._entry = entry

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{self._name}".lower()
        )

        self.description = description
        self._attr_unique_id = f"{entry.entry_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=DEFAULT_NAME,
            manufacturer="EAC",
        )

        self._attributes = {}

        _LOGGER.debug(f"Setting up EACSensor: name: {self._name} key: {self.description.key} device_class: {self.description.device_class}")

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        # d = self.coordinator.get_air_quality_value(self.entity_description.key)
        # if d and 'value' in d:
        #     return d['value']
        return 123
        return None

        
    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return self._attributes
