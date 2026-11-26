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
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import UnitOfEnergy

from .const import NAME,DOMAIN
from .coordinator import EACUpdateCoordinator

_LOGGER = logging.getLogger(__name__)



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EAC sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
  
    entities= []

    meter_readings = await coordinator.get_latest_data()
    for r in meter_readings:
        _LOGGER.debug(f"Creating sensors for spId {r.spId} with data: {r.info}")
        
        spId = r.spId
        #last_four_digits = r.spId[-4:] 

        # POV Of the user, imported energy is what we consume, exported is what we give back to the grid from Solar Panels

        if r.imp is not None:        
            name = "Consumption"
            
            entities.append(
                EACSensor(
                    entry=entry,
                    coordinator=coordinator,
                    info=r.info,
                    description=SensorEntityDescription(
                        key=f"{spId}_imp",
                        name=name,
                        device_class=SensorDeviceClass.ENERGY,
                        state_class=SensorStateClass.TOTAL_INCREASING,
                        native_unit_of_measurement="kWh",
                    )
                )
            )

        if r.exp is not None:
            name = "Production"
            
            entities.append(
                EACSensor(
                    entry=entry,
                    coordinator=coordinator,
                    info=r.info,
                    description=SensorEntityDescription(
                        key=f"{spId}_exp",
                        name=name,
                        device_class=SensorDeviceClass.ENERGY,
                        state_class=SensorStateClass.TOTAL_INCREASING,
                        native_unit_of_measurement="kWh",
                    )
                )
            )


    async_add_entities(entities)




class EACSensor(CoordinatorEntity[EACUpdateCoordinator], SensorEntity):
    """Defines a EACSensor ."""

    #_attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: EACUpdateCoordinator,
        info: dict,
        description: SensorEntityDescription
    ) -> None:
        
        """Initialize EACSensor."""
        super().__init__(coordinator)
        self._name = description.name
        self._entry = entry
        self._info = info

        self.description = description
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}-{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"{NAME} {info.get('id', '')}",
            manufacturer="EAC",
            serial_number=info.get("serialNumber", None) if info else None,
        )

        self._attributes = {
            "address": info.get("address", None) if info else None,
            "meter_id": info.get("id", None) if info else None
        }


        _LOGGER.debug(f"Setting up EACSensor: name: {self._name} key: {self.description.key} device_class: {self.description.device_class}")


    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.get_meter_value(self.description.key)

        
    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return self._attributes
