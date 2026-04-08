import re

import aiohttp
import xmltodict

METEOALARM_FEEDS = {
    "andorra": "Andorra",
    "austria": "Austria",
    "belgium": "Belgium",
    "bosnia-herzegovina": "Bosnia and Herzegovina",
    "bulgaria": "Bulgaria",
    "croatia": "Croatia",
    "cyprus": "Cyprus",
    "czechia": "Czech Republic",
    "denmark": "Denmark",
    "estonia": "Estonia",
    "finland": "Finland",
    "france": "France",
    "germany": "Germany",
    "greece": "Greece",
    "hungary": "Hungary",
    "iceland": "Iceland",
    "ireland": "Ireland",
    "israel": "Israel",
    "italy": "Italy",
    "latvia": "Latvia",
    "lithuania": "Lithuania",
    "luxembourg": "Luxembourg",
    "malta": "Malta",
    "moldova": "Moldova",
    "montenegro": "Montenegro",
    "netherlands": "Netherlands",
    "republic-of-north-macedonia": "North Macedonia",
    "norway": "Norway",
    "poland": "Poland",
    "portugal": "Portugal",
    "romania": "Romania",
    "serbia": "Serbia",
    "slovakia": "Slovakia",
    "slovenia": "Slovenia",
    "spain": "Spain",
    "sweden": "Sweden",
    "switzerland": "Switzerland",
    "ukraine": "Ukraine",
    "united-kingdom": "United Kingdom",
}


class Meteoalert:
    endpoint = "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-{0}"

    def __init__(
        self,
        country: str,
        province: str,
        language: str,
        session: aiohttp.ClientSession,
        request_timeout: float = 30.0,
    ) -> None:
        self.country = country.lower()
        self.province = province
        self.language = language or "en-GB"
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=request_timeout)
        self._ssl = True

    def set_timeout(self, seconds: float) -> None:
        self._timeout = aiohttp.ClientTimeout(total=seconds)

    async def get_provinces(self) -> dict[str, str]:
        provinces = {}

        url = self.endpoint.format(self.country)
        async with self._session.get(
            url, timeout=self._timeout, ssl=self._ssl
        ) as response:
            response.raise_for_status()
            text = await response.text()

        # Parse the XML response for the alert feed and loop over the entries
        feed_data = xmltodict.parse(text)
        feed = feed_data.get("feed", {})
        entries = feed.get("entry", [])
        entries = entries if type(entries) is list else [entries]
        for entry in entries:
            area_desc = entry.get("cap:areaDesc")
            if not area_desc:
                continue
            geocode = entry.get("cap:geocode", {})
            value_name = geocode.get("valueName")
            value = geocode.get("value")

            key = f"{value_name}:{value}" if value_name and value else area_desc
            provinces[key] = area_desc

        return provinces

    async def _fetch_alerts(self) -> list[dict]:
        """Retrieve alerts data."""
        alerts = []

        # try:
        url = self.endpoint.format(self.country)

        async with self._session.get(
            url, timeout=self._timeout, ssl=self._ssl
        ) as response:
            response.raise_for_status()
            text = await response.text()

        # Parse the XML response for the alert feed and loop over the entries
        feed_data = xmltodict.parse(text)
        feed = feed_data.get("feed", {})
        entries = feed.get("entry", [])
        entries = entries if type(entries) is list else [entries]
        for entry in entries:
            if not self._is_province_match(entry):
                continue

            # Get the cap URL for additional alert data
            cap_url = None
            for link in entry.get("link", []):
                if link.get("@type") == "application/cap+xml":
                    cap_url = link.get("@href")

            if not cap_url:
                continue

            # Parse the XML response for the alert information
            async with self._session.get(
                cap_url, timeout=self._timeout, ssl=self._ssl
            ) as response:
                response.raise_for_status()
                text = await response.text()

            alert_data = xmltodict.parse(text)
            alert = alert_data.get("alert", {})
            # Get the alert data in the requested language
            translations = alert.get("info", [])
            translations = (
                translations if type(translations) is list else [translations]
            )

            for translation in translations:
                if self.language not in translation.get("language"):
                    continue

                data = {}
                # Store alert information in the data dict
                for key, value in translation.items():
                    if type(value) is str:
                        data[key] = value

                parameters = translation.get("parameter", [])
                for parameter in parameters:
                    value_name = parameter.get("valueName")
                    value = parameter.get("value")
                    if value_name and value:
                        data[value_name] = value

                alerts.append(data)

                # Don't check other languages
                break

        return alerts

    async def get_alerts(self) -> list[dict]:
        """Retrieve all alerts."""
        return await self._fetch_alerts()

    def _is_province_match(self, entry) -> bool:

        m = re.match(r"(\w+):(\w+)", self.province)
        if m:
            # Attempt to match the province by geocode
            value_name = m.group(1)
            value = m.group(2)

            geocode = entry.get("cap:geocode", {})
            if geocode.get("valueName") == value_name and geocode.get("value") == value:
                return True

        # Fallback to attempt to match the province by regex on name
        if re.search(rf"{self.province}", entry.get("cap:areaDesc"), re.IGNORECASE):
            return True

        return False
