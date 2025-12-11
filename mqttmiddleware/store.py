"""Database-backed store for recent processed messages."""
import json
from .models import Message

def add_message(item: dict):
    """Add a processed message dict to the db.

    Expected keys: in_topic, out_topic, payload, qos, time_ms, timestamp
    """
    # payload is likely a dict or list from core.py, conv to json string
    p = item.get('payload')
    if not isinstance(p, str):
        p = json.dumps(p)

    ts = item.get('timestamp')
    if not ts:
        from datetime import datetime
        ts = datetime.utcnow()


    Message.objects.create(
        timestamp=ts,
        in_topic=item.get('in_topic'),
        out_topic=item.get('out_topic'),
        payload=p,
        qos=item.get('qos', 0),
        time_ms=item.get('time_ms', 0.0),
        status=item.get('status', '')
    )

def get_messages(limit: int = 100):
    """Return up to `limit` most recent messages."""
    return Message.objects.all()[:limit]
