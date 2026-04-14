"""Constants for the MeteoAlarm Next integration."""

DOMAIN = "meteoalarm_next"

CONF_COUNTRY = "country"
CONF_PROVINCE = "province"
CONF_LANGUAGE = "language"
CONF_COUNTRY_NAME = "country_name"
CONF_PROVINCE_NAME = "province_name"

DEFAULT_LANGUAGE = "en"

SERVICE_MANUFACTURER = "MeteoAlarm"
SERVICE_MODEL = "Legacy Atom Feed"
ATTRIBUTION = "Information provided by MeteoAlarm"

# Advanced options
CONF_UPDATE_INTERVAL_MINUTES = "update_interval_minutes"
CONF_REQUEST_TIMEOUT = "request_timeout"
DEFAULT_UPDATE_INTERVAL_MINUTES = 30
DEFAULT_REQUEST_TIMEOUT = 30  # seconds

KEY_ACTIVE_ALERTS = "active_alerts"
KEY_UPCOMING_ALERTS = "upcoming_alerts"
KEY_SUMMARY = "summary"
