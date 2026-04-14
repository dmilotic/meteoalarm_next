from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    DOMAIN,
    KEY_ACTIVE_ALERTS,
    KEY_UPCOMING_ALERTS,
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

    active_alert_entity = AlertBinarySensor(
        coordinator,
        "Active Alert",
        KEY_ACTIVE_ALERTS,
        entry_unique_id,
        child_device_info,
        BinarySensorDeviceClass.SAFETY,
    )

    upcoming_alert_entity = AlertBinarySensor(
        coordinator,
        "Upcoming Alert",
        KEY_UPCOMING_ALERTS,
        entry_unique_id,
        child_device_info,
        BinarySensorDeviceClass.SAFETY,
    )

    async_add_entities([active_alert_entity, upcoming_alert_entity])


class AlertBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: MeteoCoordinator,
        name: str,
        key: str,
        entry_unique_id: str,
        device_info: DeviceInfo,
        device_class: BinarySensorDeviceClass,
    ) -> None:
        super().__init__(coordinator)
        self._attr_attribution = ATTRIBUTION
        self._attr_has_entity_name = True
        self._attr_name = name
        self._key = key

        self._attr_unique_id = f"{entry_unique_id}_{key}"
        self._attr_device_info = device_info
        self._attr_device_class = device_class

    @property
    def is_on(self):
        data = self.coordinator.data or {}
        alerts = data.get(self._key, [])
        return len(alerts) > 0

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        alerts = data.get(self._key, [])
        return {"alerts": alerts}
