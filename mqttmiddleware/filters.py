import json
from datetime import datetime

DEFAULT_THRESHOLD = 20.0

def parse_payload(payload_bytes):
    try:
        text = payload_bytes.decode('utf-8')
    except Exception:
        return None
    # try numeric
    try:
        v = float(text)
        return {'value': v}
    except Exception:
        pass
    # try json
    try:
        j = json.loads(text)
        return j
    except Exception:
        pass
    # fallback
    return {'raw': text}

def should_forward(parsed, threshold=DEFAULT_THRESHOLD):
    if parsed is None:
        return False
    if 'value' in parsed:
        try:
            return float(parsed['value']) >= float(threshold)
        except Exception:
            return True
    return True

def map_topic(in_topic):
    # sensors/temp/device1 -> processed/temp/device1
    parts = in_topic.split('/')
    if len(parts) >= 2 and parts[0] == 'sensors':
        return 'processed/' + '/'.join(parts[1:])
    return 'processed/' + in_topic

def enrich(parsed):
    from datetime import datetime
    data = dict(parsed)
    data['processed_at'] = datetime.utcnow().isoformat() + 'Z'
    return data
