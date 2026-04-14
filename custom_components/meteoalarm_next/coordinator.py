from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import ts_util
from .const import DOMAIN, KEY_ACTIVE_ALERTS, KEY_SUMMARY, KEY_UPCOMING_ALERTS
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
        _LOGGER.debug("Fetching %s data", DOMAIN)

        local_now = dt_util.now()

        async with self._lock:
            alerts = await self._client.get_alerts()

        active_alerts = []
        upcoming_alerts = []
        active_summary = []
        upcoming_summary = []
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

            time_span = ts_util.time_span_abs(local_now, onset, expires)
            if local_now >= onset:
                active_alerts.append(alert)
                summary = f"{a_level} {a_type} {time_span}"
                summary = summary.capitalize()
                if summary not in active_summary:
                    active_summary.append(summary)
                continue

            upcoming_alerts.append(alert)
            summary = f"Upcoming {a_level} {a_type} {time_span}"
            summary = summary.capitalize()
            if summary not in upcoming_summary:
                upcoming_summary.append(summary)

        summary_list = active_summary + upcoming_summary
        data = {
            KEY_ACTIVE_ALERTS: active_alerts,
            KEY_UPCOMING_ALERTS: upcoming_alerts,
            KEY_SUMMARY: ", ".join(summary_list),
        }
        return data
