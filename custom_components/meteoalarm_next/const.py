"""Constants for the MeteoAlarm Next integration."""

DOMAIN = "meteoalarm_next"

CONF_COUNTRY = "country"
CONF_PROVINCE = "province"
CONF_LANGUAGE = "language"

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
KEY_ACTIVE_ALERT = "active_alert"
KEY_FUTURE_ALERTS = "future_alerts"
KEY_FUTURE_ALERT = "future_alert"
KEY_ACTIVE_SUMMARY = "active_summary"
KEY_FUTURE_SUMMARY = "future_summary"
