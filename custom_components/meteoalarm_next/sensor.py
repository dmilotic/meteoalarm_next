from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_COUNTRY,
    CONF_COUNTRY_NAME,
    CONF_PROVINCE,
    CONF_PROVINCE_NAME,
    DOMAIN,
    KEY_SUMMARY,
    SERVICE_MANUFACTURER,
    SERVICE_MODEL,
)
from .coordinator import MeteoCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    coordinator: MeteoCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_unique_id = entry.unique_id or entry.entry_id
    child_device_info = DeviceInfo(
        identifiers={(entry.domain, entry_unique_id)},
        name=entry.title,
        manufacturer=SERVICE_MANUFACTURER,
        model=SERVICE_MODEL,
        entry_type=DeviceEntryType.SERVICE,
    )

    summary_entity = AlertSummarySensor(
        coordinator,
        "Summary",
        KEY_SUMMARY,
        {
            CONF_COUNTRY: entry.data.get(CONF_COUNTRY),
            CONF_PROVINCE: entry.data.get(CONF_PROVINCE),
            CONF_COUNTRY_NAME: entry.data.get(CONF_COUNTRY_NAME),
            CONF_PROVINCE_NAME: entry.data.get(CONF_PROVINCE_NAME),
        },
        entry_unique_id,
        child_device_info,
    )

    async_add_entities([summary_entity])


class AlertSummarySensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: MeteoCoordinator,
        name: str,
        key: str,
        extra_attributes: dict,
        entry_unique_id: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._attr_attribution = ATTRIBUTION
        self._attr_has_entity_name = True
        self._attr_name = name
        self._key = key
        self._extra_attributes = extra_attributes

        self._attr_unique_id = f"{entry_unique_id}_{key}"
        self._attr_device_info = device_info
        self._attr_icon = "mdi:information-outline"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        value = data.get(self._key, "")
        if not value:
            return "No warnings"
        return value

    @property
    def extra_state_attributes(self):
        return self._extra_attributes or {}
