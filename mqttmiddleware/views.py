import json
from django.shortcuts import render
from . import store

def dashboard(request):
    """HTML view with charts and stats."""
    items = store.get_messages(100)
    stats = store.get_stats()

    # Prepare data for charts
    # We want a trend line of 'value' from processed messages
    labels = []
    data_values = []
    
    # Iterate in reverse to show oldest -> newest on chart
    for msg in reversed(items):
        if msg.status == 'processed':
            try:
                # payload is a stringified json like '{"value": 25.5, ...}'
                p = json.loads(msg.payload)
                val = p.get('value')
                if val is not None:
                    labels.append(msg.timestamp.strftime('%H:%M:%S'))
                    data_values.append(val)
            except Exception:
                pass

    context = {
        'messages': items,
        'stats': stats,
        'chart_labels': labels,
        'chart_data': data_values,
    }
    return render(request, 'mqttmiddleware/dashboard.html', context)
