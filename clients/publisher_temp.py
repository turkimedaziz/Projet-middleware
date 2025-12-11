"""Simple temperature publisher: publishes to sensors/temp/1 every 2s"""
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
            temp = round(random.uniform(15.0, 30.0), 2)
            client.publish('sensors/temp/1', str(temp), qos=0)
            print(f'Published temp {temp} to sensors/temp/1')
            time.sleep(2)
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
