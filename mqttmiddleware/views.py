import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from . import store
from .models import SensorConfig

def dashboard(request):
    """HTML view with charts, stats, and configuration."""
    # Handle Config Updates
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('thresh_'):
                s_type = key.replace('thresh_', '')
                try:
                    val = float(value)
                    SensorConfig.objects.update_or_create(
                        sensor_type=s_type,
                        defaults={'threshold': val}
                    )
                except ValueError:
                    pass
        return redirect('dashboard')

    # Fetch Configs (create defaults if missing)
    if not SensorConfig.objects.exists():
        SensorConfig.objects.create(sensor_type='temp', threshold=20.0)
        SensorConfig.objects.create(sensor_type='hum', threshold=40.0)
    
    configs = SensorConfig.objects.all()

    items = store.get_messages(100)
    stats = store.get_stats()

    # Prepare data for charts
    temp_labels = []
    temp_data = []
    hum_labels = []
    hum_data = []
    
    # Iterate in reverse to show oldest -> newest on chart
    for msg in reversed(items):
        if msg.status == 'processed':
            try:
                # payload is a stringified json like '{"value": 25.5, ...}'
                p = json.loads(msg.payload)
                val = p.get('value')
                if val is not None:
                    ts = msg.timestamp.strftime('%H:%M:%S')
                    if 'temp' in msg.in_topic:
                        temp_labels.append(ts)
                        temp_data.append(val)
                    elif 'hum' in msg.in_topic:
                        hum_labels.append(ts)
                        hum_data.append(val)
            except Exception:
                pass

    if request.GET.get('api'):
        html = render_to_string('mqttmiddleware/partials/table_rows.html', {'messages': items}, request=request)
        return JsonResponse({
            'stats': stats,
            'temp_labels': temp_labels,
            'temp_data': temp_data,
            'hum_labels': hum_labels,
            'hum_data': hum_data,
            'table_html': html
        })

    context = {
        'messages': items,
        'stats': stats,
        'configs': configs,
        'temp_labels': temp_labels,
        'temp_data': temp_data,
        'hum_labels': hum_labels,
        'hum_data': hum_data,
    }
    return render(request, 'mqttmiddleware/dashboard.html', context)
