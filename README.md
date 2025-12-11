# MQTT Middleware Django Demo

This demo implements a small MQTT middleware inside a Django project. It subscribes to `sensors/#`, optionally filters/ enriches messages, logs them to `logs/middleware.log` and republishes to `processed/#`.

Prereqs
- Python 3.8+
- Mosquitto (or any MQTT broker)

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Mosquitto (Debian/Ubuntu):

```bash
sudo apt update
sudo apt install -y mosquitto
sudo systemctl enable --now mosquitto
```

Start Mosquitto in foreground (for demo):

```bash
# Start broker in a terminal
sudo systemctl stop mosquitto
mosquitto -v
```

Run the middleware (Django management command):

```bash
# in project root
python manage.py runmiddleware --host localhost --port 1883 --threshold 20 --qos 0
```

Start the publisher(s) in separate terminals:

```bash
python clients/publisher_temp.py --host localhost --port 1883
python clients/publisher_hum.py --host localhost --port 1883
```

Start subscribers to watch the flow:

```bash
python clients/subscriber_raw.py --host localhost --port 1883
python clients/subscriber_processed.py --host localhost --port 1883
```

What to demo
- Start Mosquitto
- Start middleware
- Start publishers
- Start subscribers
- Change the middleware threshold (stop and restart with a lower `--threshold`) and observe filtered messages

Logs are written to `logs/middleware.log`.
# Projet-middleware-