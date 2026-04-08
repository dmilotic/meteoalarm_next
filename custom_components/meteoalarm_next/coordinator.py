from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    KEY_ACTIVE_ALERT,
    KEY_ACTIVE_ALERTS,
    KEY_ACTIVE_SUMMARY,
    KEY_FUTURE_ALERT,
    KEY_FUTURE_ALERTS,
    KEY_FUTURE_SUMMARY,
)
from .meteoalertapi import Meteoalert

_LOGGER = logging.getLogger(__name__)


class MeteoCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        interval_min: int,
        client: Meteoalert,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval_min),
        )
        self._client = client
        self._lock = asyncio.Lock()

    async def _async_update_data(self) -> dict:
        _LOGGER.debug("Fetching HEP ODS data")

        local_now = dt_util.now()

        async with self._lock:
            alerts = await self._client.get_alerts()

        active_alerts = []
        future_alerts = []
        active_summary = []
        future_summary = []
        for alert in alerts:
            onset = dt_util.parse_datetime(alert.get("onset", ""))
            expires = dt_util.parse_datetime(alert.get("expires", ""))
            if not onset or not expires:
                continue
            onset = dt_util.as_local(onset)
            expires = dt_util.as_local(expires)
            if local_now > expires:
                continue

            a_level: str = alert.get("awareness_level", "")
            a_level = a_level.rsplit(";", maxsplit=1)[-1]
            a_level = a_level.strip()
            a_type: str = alert.get("awareness_type", "")
            a_type = a_type.rsplit(";", maxsplit=1)[-1]
            a_type = a_type.replace("-", " ")
            a_type = a_type.strip()

            if local_now > onset:
                active_alerts.append(alert)
                diff = expires - local_now
                hours = round(diff.total_seconds() / 3600)
                summary = f"{a_level} {a_type} for {hours}h"
                summary = summary.capitalize()
                if summary not in active_summary:
                    active_summary.append(summary)
                continue

            future_alerts.append(alert)
            diff = onset - local_now
            hours = round(diff.total_seconds() / 3600)
            summary = f"{a_level} {a_type} in {hours}h"
            summary = summary.capitalize()
            if summary not in active_summary:
                future_summary.append(summary)

        active_alert = len(active_alerts) > 0
        future_alert = len(future_alerts) > 0

        data = {
            KEY_ACTIVE_ALERTS: active_alerts,
            KEY_FUTURE_ALERTS: future_alerts,
            KEY_ACTIVE_ALERT: active_alert,
            KEY_FUTURE_ALERT: future_alert,
            KEY_ACTIVE_SUMMARY: ", ".join(active_summary),
            KEY_FUTURE_SUMMARY: ", ".join(future_summary),
        }
        return data
