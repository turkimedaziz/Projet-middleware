"""Simple humidity publisher: publishes to sensors/hum/2 every 3s"""
import time
import random
import argparse
import paho.mqtt.client as mqtt

def run(broker='localhost', port=1883):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    client.loop_start()
    try:
        while True:
            hum = round(random.uniform(30.0, 90.0), 2)
            client.publish('sensors/hum/2', str(hum), qos=0)
            print(f'Published hum {hum} to sensors/hum/2')
            time.sleep(3)
    except KeyboardInterrupt:
        print('Stopping publisher')
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=1883)
    args = parser.parse_args()
    run(broker=args.host, port=args.port)
