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
    DOMAIN,
    KEY_ACTIVE_SUMMARY,
    KEY_FUTURE_SUMMARY,
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

    active_alert_entity = AlertSummarySensor(
        coordinator,
        "Active Summary",
        KEY_ACTIVE_SUMMARY,
        [],
        child_device_info,
        entry_unique_id,
    )

    future_alert_entity = AlertSummarySensor(
        coordinator,
        "Future Summary",
        KEY_FUTURE_SUMMARY,
        [],
        child_device_info,
        entry_unique_id,
    )

    async_add_entities([active_alert_entity, future_alert_entity])


class AlertSummarySensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: MeteoCoordinator,
        name: str,
        key: str,
        extra_attributes: list[str],
        device_info: DeviceInfo,
        entry_unique_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_attribution = ATTRIBUTION
        self._attr_has_entity_name = True
        self._attr_name = name
        self._key = key
        self._extra_attributes = extra_attributes
        self._attr_icon = "mdi:information-outline"

        self._attr_device_info = device_info
        self._attr_unique_id = f"{entry_unique_id}_{key}"

    @property
    def native_value(self):
        data = self.coordinator.data or {}

        value = data.get(self._key)
        if value == "":
            return "No warnings"
        return value

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {k: data.get(k) for k in self._extra_attributes}
