from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.selector import selector
from homeassistant.util import slugify

from .const import (
    CONF_COUNTRY,
    CONF_COUNTRY_NAME,
    CONF_LANGUAGE,
    CONF_PROVINCE,
    CONF_PROVINCE_NAME,
    CONF_REQUEST_TIMEOUT,
    CONF_UPDATE_INTERVAL_MINUTES,
    DEFAULT_LANGUAGE,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
)
from .meteoalertapi import METEOALARM_FEEDS, Meteoalert


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._country: str = ""
        self._provinces: dict
        self._province: str
        self._language: str

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            try:
                self._country = user_input[CONF_COUNTRY]

                session = aiohttp_client.async_get_clientsession(self.hass)
                client = Meteoalert(
                    country=self._country,
                    province="",
                    language="",
                    session=session,
                )
                self._provinces = await client.get_provinces()
                return await self.async_step_select_province()
            except Exception as e:  # noqa: BLE001
                errors["base"] = repr(e)

        country_options = [
            {
                "value": key,
                "label": value,
            }
            for key, value in METEOALARM_FEEDS.items()
        ]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_COUNTRY, default=self._country): selector(
                    {
                        "select": {
                            "options": country_options,
                            "mode": "dropdown",
                            "custom_value": True,
                        }
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_select_province(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._province = user_input[CONF_PROVINCE]
            self._language = user_input[CONF_LANGUAGE]

            unique_id = slugify(f"{self._country} {self._province}")
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            country_name = METEOALARM_FEEDS.get(self._country, self._country)
            province_name = self._provinces.get(self._province, self._province)
            title = f"MeteoAlarm {str.capitalize(country_name)} - {province_name}"
            return self.async_create_entry(
                title=title,
                data={
                    CONF_COUNTRY: self._country,
                    CONF_PROVINCE: self._province,
                    CONF_LANGUAGE: self._language,
                    CONF_COUNTRY_NAME: country_name,
                    CONF_PROVINCE_NAME: province_name,
                },
                options={
                    CONF_UPDATE_INTERVAL_MINUTES: DEFAULT_UPDATE_INTERVAL_MINUTES,
                    CONF_REQUEST_TIMEOUT: DEFAULT_REQUEST_TIMEOUT,
                },
            )

        province_options = [
            {
                "value": key,
                "label": value,
            }
            for key, value in sorted(self._provinces.items())
        ]

        language_options = [DEFAULT_LANGUAGE]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_PROVINCE): selector(
                    {
                        "select": {
                            "options": province_options,
                            "mode": "dropdown",
                            "custom_value": True,
                        }
                    }
                ),
                vol.Required(CONF_LANGUAGE): selector(
                    {
                        "select": {
                            "options": language_options,
                            "mode": "dropdown",
                            "custom_value": True,
                        }
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="select_province",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL_MINUTES,
                    default=options.get(
                        CONF_UPDATE_INTERVAL_MINUTES, DEFAULT_UPDATE_INTERVAL_MINUTES
                    ),
                ): vol.Coerce(int),
                vol.Optional(
                    CONF_REQUEST_TIMEOUT,
                    default=options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT),
                ): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
