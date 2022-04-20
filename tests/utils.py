import datetime
from typing import Optional


def get_logstream_dummy_events(count: int = 5, log_datetime: Optional[datetime.datetime] = None):
    if not log_datetime:
        ts = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)).timestamp() * 1000
    else:
        ts = log_datetime.timestamp() * 1000
    events = []
    for i in range(count):
        event = {
            "timestamp": int(ts),
            "message": f"message-{i}",
        }
        events.append(event)
    return events
