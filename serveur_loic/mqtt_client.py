# mqtt_client.py
import json
from typing import Callable

import paho.mqtt.client as mqtt

from config import MQTT_HOST, MQTT_PORT, TOPIC_GAME_STATUS


class MqttClient:
    def __init__(
        self,
        on_game_status: Callable[[str, bool], None],
        on_connect_change: Callable[[bool], None],
    ):
        self._client = mqtt.Client()
        self._on_game_status = on_game_status
        self._on_connect_change = on_connect_change

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    def start(self):
        self._client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        self._client.loop_start()

    def stop(self):
        self._client.loop_stop()
        self._client.disconnect()

    # ---------- Callbacks MQTT ----------

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._client.subscribe(TOPIC_GAME_STATUS)
            self._on_connect_change(True)
        else:
            self._on_connect_change(False)

    def _on_disconnect(self, client, userdata, rc):
        self._on_connect_change(False)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            session_id = payload.get("sessionId")
            state = payload.get("state")
            if state == "SUCCESS":
                self._on_game_status(session_id, True)
            elif state == "FAIL":
                self._on_game_status(session_id, False)
        except Exception as ex:
            print("Erreur message MQTT:", ex)

    def publish(self, topic: str, payload: dict):
        self._client.publish(topic, json.dumps(payload), qos=0, retain=False)
