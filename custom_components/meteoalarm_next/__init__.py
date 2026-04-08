from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_COUNTRY,
    CONF_LANGUAGE,
    CONF_PROVINCE,
    CONF_REQUEST_TIMEOUT,
    CONF_UPDATE_INTERVAL_MINUTES,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
)
from .coordinator import MeteoCoordinator
from .meteoalertapi import Meteoalert

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = entry.data
    options = entry.options or {}
    request_timeout = int(options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT))

    session_mjerenje = aiohttp_client.async_get_clientsession(hass)
    client = Meteoalert(
        country=data[CONF_COUNTRY],
        province=data[CONF_PROVINCE],
        language=data[CONF_LANGUAGE],
        session=session_mjerenje,
        request_timeout=request_timeout,
    )

    interval_min = int(
        options.get(CONF_UPDATE_INTERVAL_MINUTES, DEFAULT_UPDATE_INTERVAL_MINUTES)
    )
    coordinator = MeteoCoordinator(hass, interval_min, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    hass.config_entries.async_schedule_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    pass
