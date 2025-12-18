import json
import time
import threading
import paho.mqtt.client as mqtt
from .filters import parse_payload, should_forward, map_topic, enrich
from .logger import setup_logger
from . import store
from .models import SensorConfig
from django.conf import settings

class Middleware:
    def __init__(self, broker_host='localhost', broker_port=1883, threshold=20.0, qos=0):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.threshold = threshold
        self.qos = qos
        self.client = mqtt.Client()
        self.logger = setup_logger()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self):
        self.client.connect(self.broker_host, self.broker_port, 60)
        # run loop in background thread
        thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        thread.start()
        self.logger.info('Middleware started, connected to %s:%d', self.broker_host, self.broker_port)
        # keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Middleware stopping...')
            self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info('Connected with result code %s', rc)
        # subscribe to sensors/#
        client.subscribe('sensors/#')
        self.logger.info('Subscribed to sensors/#')

    def on_message(self, client, userdata, msg):
        start = time.time()
        topic = msg.topic
        payload = msg.payload
        qos = msg.qos

        parsed = parse_payload(payload)
        
        # Dynamic Threshold Lookup
        current_threshold = self.threshold # fallback
        s_type = None
        if 'temp' in topic:
            s_type = 'temp'
        elif 'hum' in topic:
            s_type = 'hum'
        
        if s_type:
            try:
                # Query DB for dynamic config
                # Note: DB queries on every message might be slow in production, but OK for demo.
                # Consider caching in a real app.
                conf = SensorConfig.objects.filter(sensor_type=s_type).first()
                if conf:
                    current_threshold = conf.threshold
            except Exception as e:
                pass

        forwarded = should_forward(parsed, threshold=current_threshold)

        if not forwarded:
            self.logger.info('Filtered out message on %s payload=%s qos=%s', topic, payload, qos)
            # record filtered item as well (optional)
            try:
                store.add_message({
                    'in_topic': topic,
                    'out_topic': None,
                    'payload': parsed,
                    'qos': qos,
                    'time_ms': (time.time() - start) * 1000.0,
                    'status': 'filtered',
                })
            except Exception:
                pass
            return

        out_topic = map_topic(topic)
        enriched = enrich(parsed)
        out_payload = json.dumps(enriched)

        # publish
        client.publish(out_topic, out_payload, qos=self.qos)

        elapsed = (time.time() - start) * 1000.0
        self.logger.info('Processed: in_topic=%s out_topic=%s qos=%s time_ms=%.2f payload=%s', topic, out_topic, qos, elapsed, out_payload)
        # store the processed message for dashboard
        try:
            store.add_message({
                'in_topic': topic,
                'out_topic': out_topic,
                'payload': enriched,
                'qos': qos,
                'time_ms': elapsed,
                'status': 'processed',
            })
        except Exception:
            pass
