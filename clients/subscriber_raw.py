"""Subscriber that listens to sensors/# and prints raw messages"""
import argparse
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print('Connected, subscribing to sensors/#')
    client.subscribe('sensors/#')

def on_message(client, userdata, msg):
    print(f'RAW {msg.topic} qos={msg.qos} payload={msg.payload.decode("utf-8", "ignore")}')

def run(broker='localhost', port=1883):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, 60)
    client.loop_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=1883)
    args = parser.parse_args()
    run(broker=args.host, port=args.port)
