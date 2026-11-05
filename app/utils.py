from datetime import datetime, timezone


def utc_now_iso():
    """Return the current UTC time as an ISO-8601 string with a 'Z' suffix."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
