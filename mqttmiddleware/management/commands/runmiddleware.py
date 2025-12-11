from django.core.management.base import BaseCommand
from mqttmiddleware.core import Middleware


class Command(BaseCommand):
    help = 'Run the MQTT middleware loop'

    def add_arguments(self, parser):
        parser.add_argument('--host', default='localhost', help='MQTT broker host')
        parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
        parser.add_argument('--threshold', type=float, default=20.0, help='Forward threshold for numeric values')
        parser.add_argument('--qos', type=int, default=0, choices=[0,1], help='QoS to use when republishing')

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        threshold = options['threshold']
        qos = options['qos']

        mw = Middleware(broker_host=host, broker_port=port, threshold=threshold, qos=qos)
        self.stdout.write(self.style.SUCCESS(f'Starting middleware connecting to {host}:{port} threshold={threshold} qos={qos}'))
        mw.start()
