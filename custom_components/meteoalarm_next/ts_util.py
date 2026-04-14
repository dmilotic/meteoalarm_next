from datetime import datetime, timedelta
import math


def time_span_rel(now: datetime, onset: datetime, expires: datetime) -> str:
    if now > expires:
        return ""
    if now > onset:
        diff = expires - now
        hours = math.ceil(diff.total_seconds() / 3600)
        time_span = f"for {hours}h"
        return time_span

    diff = onset - now
    hours = math.ceil(diff.total_seconds() / 3600)
    time_span = f"in {hours}h"
    return time_span


def time_span_abs(now: datetime, onset: datetime, expires: datetime) -> str:
    if now > expires:
        return ""
    if now > onset:
        date_str = expires.strftime("%d.%m.")
        if now.date() == expires.date():
            date_str = "today"
        elif now.date() == expires.date() + timedelta(days=1):
            date_str = "tomorrow"

        time_str = expires.strftime("%H:%M")
        if _can_round_hour(expires):
            time_str = _format_round_hour(expires)

        time_span = f"until {date_str} {time_str}"
        return time_span

    time_span = (
        f"for {onset.strftime('%d.%m. %H:%M')}-{expires.strftime('%d.%m. %H:%M')}"
    )
    if onset.date() == expires.date():
        date_str = onset.strftime("%d.%m.")
        if now.date() == onset.date():
            date_str = "today"
        elif now.date() == onset.date() + timedelta(days=1):
            date_str = "tomorrow"

        time_str = f"{onset.strftime('%H:%M')}-{expires.strftime('%H:%M')}"
        if _can_round_hour(onset) and _can_round_hour(expires):
            time_str = f"{_format_round_hour(onset)}-{_format_round_hour(expires)}"

        time_span = f"for {date_str} {time_str}"

    return time_span


def _can_round_hour(d: datetime) -> bool:
    if d.minute == 59:
        d += timedelta(minutes=1)
    return d == d.replace(minute=0, second=0, microsecond=0)


def _format_round_hour(d: datetime) -> str:
    if d.minute == 59:
        d += timedelta(minutes=1)
    return d.strftime("%Hh")
