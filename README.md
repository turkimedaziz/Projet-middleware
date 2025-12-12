
# MQTT Middleware Django Demo — Full Guide

This repository implements a lightweight MQTT middleware inside a small Django project. It demonstrates how to subscribe to MQTT topics, filter and transform messages, log and persist them, and republish to processed topics. A small dashboard (Django view) shows recent messages in real time.

Contents of this README
- Architecture overview
- Files and what each does
- Setup (virtualenv, dependencies, Mosquitto)
- Run sequence (terminals to open, commands)
- How the middleware processes messages (logic & filters)
- Dashboard and persistence
- Tips, debugging, and next steps

## Architecture (high level)

Devices/publishers -> MQTT Broker (Mosquitto) -> Middleware (Django management command) -> processed topics -> Subscribers / Dashboard

- Broker: Mosquitto (or any MQTT broker) routes messages.
- Middleware: subscribes to `sensors/#`, filters/converts payloads, logs, persists, and republishes to `processed/<...>`.
- Clients: simple publisher and subscriber scripts under `clients/` for demo.
- Dashboard: a Django view at `/` (or `/dashboard/`) showing recent messages.

## Files and purpose (what was added)

Top-level
- `manage.py` — Django entry point. Use it to run the middleware (`runmiddleware`) and `runserver` for the dashboard.
- `requirements.txt` — Python dependencies (Django, paho-mqtt).
- `README.md` — this document.
- `logs/middleware.log` — middleware writes runtime logs here.

`proj/` (Django project)
- `proj/settings.py` — minimal settings (SQLite DB, app registration, `LOG_DIR`).
- `proj/urls.py` — routes root `/` and `/dashboard/` to the dashboard view.
- `proj/wsgi.py` — WSGI entry for completeness.

`mqttmiddleware/` (Django app / middleware logic)
- `apps.py` — Django AppConfig.
- `core.py` — Middleware core logic (MQTT client using paho-mqtt). Responsibilities:
	- Connect to broker and subscribe to `sensors/#`.
	- Parse payloads, apply `filters.should_forward`.
	- Map input topics to `processed/...` using `filters.map_topic`.
	- Enrich payloads (add `processed_at`) and republish to `processed/...`.
	- Log processing time and decisions.
	- Persist processed messages to the DB (so dashboard and other processes can read them).
- `filters.py` — small utilities:
	- `parse_payload`: decode payloads (float, json, or raw string).
	- `should_forward`: simple numeric threshold filter (drop values < threshold).
	- `map_topic`: convert `sensors/...` -> `processed/...`.
	- `enrich`: add `processed_at` timestamp.
- `logger.py` — sets up a file logger writing to `logs/middleware.log`.
- `store.py` — an in-memory thread-safe deque used to keep recent messages inside the middleware process (useful for quick debugging and fallback). Note: dashboard reads from DB, not this store.
- `views.py` — dashboard view. Initially read from in-memory store; later updated to read from DB (see `models.py`). Renders a simple auto-refresh HTML table.
- `models.py` — `MiddlewareMessage` model to persist processed/filtered messages (fields: timestamp, status, in_topic, out_topic, payload JSON, qos, time_ms).
- `management/commands/runmiddleware.py` — Django management command to run the middleware loop. Use `python manage.py runmiddleware`.

`clients/` (demo scripts)
- `publisher_temp.py` — publishes temperature values to `sensors/temp/1` every 2s.
- `publisher_hum.py` — publishes humidity values to `sensors/hum/2` every 3s.
- `subscriber_raw.py` — subscribes to `sensors/#` and prints raw messages.
- `subscriber_processed.py` — subscribes to `processed/#` and prints processed messages.

## Setup (recommended, safe)

1) Create and activate a virtual environment (recommended to avoid system package issues):

```bash
cd ~/proj-sd
python3 -m venv .venv
source .venv/bin/activate
```

2) Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Install Mosquitto (Debian/Ubuntu example). If you already have a broker, skip this.

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

4) Create database migrations for the middleware model and apply them:

```bash
python manage.py makemigrations mqttmiddleware
python manage.py migrate
```

## Run sequence (terminals)

Open separate terminals (or tmux panes). In each terminal, activate the venv with `source .venv/bin/activate` before running commands.

1) Start Mosquitto (if not running as a service):

```bash
# run in foreground to see broker logs
mosquitto -v
```

2) Start the middleware (this is the core program that subscribes to the broker):

```bash
python manage.py runmiddleware --host localhost --port 1883 --threshold 20 --qos 0
```

Flags:
- `--host`, `--port`: broker location.
- `--threshold`: numeric threshold used by `filters.should_forward` (default 20.0).
- `--qos`: QoS used when republishing (0 or 1).

3) Start the dashboard (Django development server):

```bash
python manage.py runserver 8000
# then open http://127.0.0.1:8000/ in your browser
```

4) Start demo publishers (in separate terminals):

```bash
python clients/publisher_temp.py --host localhost --port 1883
python clients/publisher_hum.py --host localhost --port 1883
```

5) (Optional) Start raw subscriber to observe incoming sensor messages:

```bash
python clients/subscriber_raw.py --host localhost --port 1883
```

6) Watch the dashboard at `http://127.0.0.1:8000/` — it auto-refreshes every 2 seconds.

## How middleware processes messages (detailed)

1. The middleware (`mqttmiddleware/core.py`) connects to the broker using `paho-mqtt` and subscribes to `sensors/#`.
2. On message arrival, `filters.parse_payload` tries to decode the payload as a float, then as JSON; otherwise keeps it as a string.
3. `filters.should_forward` checks numeric values against the configured `threshold`; non-numeric messages pass through by default.
4. If the message is forwarded, `filters.map_topic` maps `sensors/<rest>` -> `processed/<rest>`.
5. `filters.enrich` appends `processed_at` timestamp to the message payload.
6. The middleware republishes the enriched JSON to the `processed/...` topic and logs the action.
7. The middleware persists the message to the `MiddlewareMessage` DB model (so the dashboard and other processes can read it).

If a message is filtered, the middleware logs that decision and still records a `filtered` entry in the DB.

## Dashboard and persistence

- The dashboard is a plain HTML view implemented in `mqttmiddleware/views.py` and served by Django's runserver. It queries the `MiddlewareMessage` table and displays the most recent rows.
- We persist messages to the SQLite DB (default Django dev database) so the dashboard (a separate process) can display messages independent of middleware process memory.

## Logs

- `logs/middleware.log` contains INFO messages about connections, processed messages, filter decisions, and processing times.
- Tail logs with:

```bash
tail -f logs/middleware.log
```

## Debugging checklist (if something is empty / not working)

- No messages on dashboard: ensure the middleware is running and that the DB migrations were applied. Check the middleware terminal for errors and `logs/middleware.log` for recent activity.
- Publishers exit with errors: make sure `.venv` is activated and `paho-mqtt` is installed; confirm Mosquitto is running and reachable at the host/port used.
- Dashboard not reachable: confirm `python manage.py runserver` is running and serving at 127.0.0.1:8000.

Useful checks:

```bash
# check broker
ss -ltnp | grep 1883
# check processes
ps aux | grep mosquitto
# check DB entries
python manage.py shell -c "from mqttmiddleware.models import MiddlewareMessage; print(MiddlewareMessage.objects.count())"
```

## Extending the demo (next steps)

- QoS demo: add `--qos` flags to publishers and run middleware with QoS 1 to demonstrate at-least-once delivery.
- Real-time dashboard: replace meta-refresh with Server-Sent Events (SSE) or WebSockets for instant UI updates.
- Persistence and retention: add a management command to purge old messages, or store messages in a more scalable store (Postgres, Redis).
- Admin UI: register `MiddlewareMessage` in Django admin for richer browsing.

## Implementation notes and safety

- This project uses Django for convenience (management commands, ORM, templating). The middleware logic itself is in `mqttmiddleware/core.py` and can be refactored into a standalone service if needed.
- The Django development server and the bundled SQLite database are fine for demos and development; for production use a proper WSGI server and production database.
- The middleware is defensive: DB write failures are logged but don't crash message processing.

## Quick copy-paste run (all in separate terminals)

Terminal 1: Broker (foreground)
```bash
mosquitto -v
```

Terminal 2: Middleware
```bash
source .venv/bin/activate
python manage.py runmiddleware --host localhost --port 1883 --threshold 20 --qos 0
```

Terminal 3: Dashboard
```bash
source .venv/bin/activate
python manage.py runserver 8000
```

Terminal 4/5: Publishers
```bash
source .venv/bin/activate
python clients/publisher_temp.py --host localhost --port 1883
python clients/publisher_hum.py --host localhost --port 1883
```

Terminal 6 (optional): Raw subscriber
```bash
python clients/subscriber_raw.py --host localhost --port 1883
```

Open your browser to http://127.0.0.1:8000/ and watch messages arrive.

---

