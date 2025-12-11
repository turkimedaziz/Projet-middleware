"""In-memory thread-safe store for recent processed messages."""
from collections import deque
from threading import Lock
from datetime import datetime

_MAX = 200
_dq = deque(maxlen=_MAX)
_lock = Lock()

def add_message(item: dict):
    """Add a processed message dict to the store.

    Expected keys: in_topic, out_topic, payload, qos, time_ms, timestamp
    """
    if 'timestamp' not in item:
        item['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    with _lock:
        _dq.appendleft(item)

def get_messages(limit: int = 100):
    """Return up to `limit` most recent messages as a list (newest first)."""
    with _lock:
        return list(_dq)[:limit]
