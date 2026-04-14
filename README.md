# MeteoAlarm Next – Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/dmilotic/meteoalarm_next.svg)](https://github.com/dmilotic/meteoalarm_next/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant integration for weather warnings from [MeteoAlarm](https://www.meteoalarm.org/). A modern, UI-configurable replacement for the [built-in MeteoAlarm integration](https://www.home-assistant.io/integrations/meteoalarm/) in Home Assistant core. Fetches active and upcoming alerts for a selected country and province via the MeteoAlarm legacy Atom feed. Supports 38 European countries.

The built-in integration uses YAML configuration, exposes only a single binary sensor per entry, and silently drops all but the first active warning when multiple warnings are issued simultaneously. This integration addresses all three limitations.

## Features

- **Active & upcoming alerts** – binary sensors that trigger when warnings are in effect or approaching
- **Alert summaries** – human-readable text sensor listing current and upcoming warnings (e.g. `Yellow wind for 3h, Upcoming orange rain in 2h`)
- **Per-province filtering** – select a specific region within a country
- **Full alert attributes** – each binary sensor exposes the raw alert list as attributes (awareness level, type, onset, expires, description)
- **Configurable update interval** – default 30 minutes, adjustable in options

## Installation

### HACS (Recommended)

1. Install HACS if you don't have it already
2. Open HACS in Home Assistant → Integrations
3. Click ⋮ (three dots) in the top right → **Custom repositories**
4. Add repository: `https://github.com/dmilotic/meteoalarm_next`, category **Integration**
5. Search for **MeteoAlarm Next** and install it
6. Restart Home Assistant

### Manual Installation

1. Download the latest [release](https://github.com/dmilotic/meteoalarm_next/releases)
2. Copy the `meteoalarm_next` directory to `config/custom_components/`
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **MeteoAlarm Next**
3. Select your country from the dropdown
4. Select your province/region from the dropdown
5. Select the language for alert descriptions (currently `en`)
6. *(Optional)* Click **Configure** to adjust the update interval and request timeout

## Entities

Each configured country/province creates one device with three entities.

### Binary Sensors

| Entity | Device Class | Description |
|--------|-------------|-------------|
| `Active Alert` | `safety` | `on` when at least one alert is currently active |
| `Upcoming Alert` | `safety` | `on` when at least one alert starts in the future |

Both binary sensors expose an `alerts` attribute containing the full list of matching alerts. Each alert includes fields such as `awareness_level`, `awareness_type`, `onset`, `expires`, `event`, `description`, and `instruction`.

### Sensors

| Entity | Description |
|--------|-------------|
| `Summary` | Comma-separated summary of all alerts (e.g. `Yellow wind for 3h, Upcoming orange rain in 2h`) or `No warnings` |

## Supported Countries

Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Iceland, Ireland, Israel, Italy, Latvia, Lithuania, Luxembourg, Malta, Moldova, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Ukraine, United Kingdom.

## Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.meteoalarm_next: debug
```

## Troubleshooting

**No alerts appear** – verify that MeteoAlarm publishes warnings for your selected province. During calm weather periods the feed may be empty and both binary sensors will be `off`.

**Province not found** – the province list is populated live from the feed on setup. If the feed is temporarily unavailable, setup will fail. Retry after a few minutes.

**Alert language unavailable** – if the requested language is not present in a given alert, that alert is skipped. Currently only `en` is guaranteed to be available across all feeds.

## Acknowledgements

This integration was developed with reference to two prior open-source projects, both released under the MIT License:

- [home-assistant/core – meteoalarm](https://github.com/home-assistant/core/tree/dev/homeassistant/components/meteoalarm) – the built-in Home Assistant MeteoAlarm integration (originally contributed by Rolf Berkenbosch)
- [rolfberkenbosch/meteoalert-api](https://github.com/rolfberkenbosch/meteoalert-api) – the Python wrapper for the MeteoAlarm feed by Rolf Berkenbosch, which the built-in integration depends on

## Notes

*This integration is not affiliated with EUMETNET or MeteoAlarm. It uses the publicly available MeteoAlarm legacy Atom feed (`feeds.meteoalarm.org`) and may stop working if the feed format changes.*

## License

[MIT License](LICENSE)
