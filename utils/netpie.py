import json

import paho.mqtt.client as mqtt

from core.config import Config

netpie_host = "broker.netpie.io"
client_id = Config.NETPIE_CLIENT_ID
token = Config.NETPIE_TOKEN
secret = Config.NETPIE_SECRET


def on_connect(client, userdata, flags, rc, properties=None):
    pass


try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
except AttributeError:
    client = mqtt.Client(client_id=client_id)

client.username_pw_set(token, secret)
client.on_connect = on_connect

client.connect(netpie_host, 1883, 60)
client.loop_start()


def mqtt_send(topic: str, payload: dict):
    try:
        # print(f"Topic: {topic}, Payload: {payload}")
        msg = json.dumps(payload)
        result = client.publish(topic, msg)
        status = result[0]

        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
    except Exception as e:
        print(f"Error: {e}")
        client.loop_stop()
        client.disconnect()
