from django.http import HttpResponse
from django.utils.html import escape
from . import store

def dashboard(request):
    """Simple HTML view showing recent middleware messages."""
    items = store.get_messages(100)
    rows = []
    for it in items:
        in_t = escape(str(it.in_topic))
        out_t = escape(str(it.out_topic or ''))
        payload = escape(str(it.payload))
        qos = escape(str(it.qos))
        time_ms = escape(f"{it.time_ms:.2f}")
        ts = escape(str(it.timestamp))
        status = escape(str(it.status))
        rows.append(f"<tr><td>{ts}</td><td>{status}</td><td>{in_t}</td><td>{out_t}</td><td>{qos}</td><td>{time_ms}</td><td>{payload}</td></tr>")

    html = f"""
<html>
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="2">
  <title>MQTT Middleware Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 12px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 6px; font-size: 14px; }}
    th {{ background: #f4f4f4; text-align: left; }}
    tr:nth-child(even) {{ background: #fbfbfb; }}
    .small {{ font-size: 12px; color: #666; }}
  </style>
</head>
<body>
  <h2>MQTT Middleware - Recent Messages</h2>
  <p class="small">Auto-refreshes every 2s. Showing up to 100 most recent messages.</p>
  <table>
    <thead>
      <tr><th>timestamp</th><th>status</th><th>in_topic</th><th>out_topic</th><th>qos</th><th>time_ms</th><th>payload</th></tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    return HttpResponse(html)
