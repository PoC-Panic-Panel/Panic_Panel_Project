import json
import threading
import paho.mqtt.client as mqtt

class MQTTClientWrapper:
    def __init__(self, host="192.168.1.97", port=1883, topic="panic/server/session"):
        self.host = host
        self.port = port
        self.topic = topic
        self.sessionID = ""
        self.messages = []

        # Event pour message "Start"
        self.start_event = threading.Event()

        # MQTT client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.user_data_set(self.messages)

        # Callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe

    # ------------------ CALLBACKS ------------------

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"❌ Échec connexion : {reason_code}.")
        else:
            print("✅ Connecté, abonnement…")
            client.subscribe(self.topic, qos=1)

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print(f"❌ Abonnement rejeté : {reason_code_list[0]}")
        else:
            print(f"📡 Abonnement réussi, QoS = {reason_code_list[0].value}")

    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
            print("🔕 Désabonnement réussi")
        else:
            print(f"❌ Échec du désabonnement : {reason_code_list[0]}")
        client.disconnect()

    def on_message(self, client, userdata, message):
        try:
            text = message.payload.decode("utf-8")
            print(f"📩 Message brut reçu : {text}")

            payload = json.loads(text)

            if "games" not in payload:
                print("⚠️ Le JSON ne contient pas 'games'")
                return
            
            self.sessionID = payload["sessionId"]

            games = payload["games"]

            if "rfid_memory" in games:
                print("🟢 La partie commence")
                self.start_event.set()
            else: 
                print("⏳ En attente...")
        
        except Exception as e:
            print(f"❌ Erreur dans on_message : {e}")


    # ------------------ MÉTHODE BLOQUANTE ------------------

    def wait_for_start(self, timeout=None) -> bool:
        """
        Bloque jusqu'à la réception du message.
        Retourne True si reçu, False si timeout.
        """
        print("⏳ En attente du message START…")
        received = self.start_event.wait(timeout=timeout)
        if received:
            print("🟢 START détecté, on continue !")
        else:
            print("⛔ Timeout sans recevoir START.")
        return received

    # ------------------ MQTT CONTROL ------------------

    def start(self):
        print(f"Connexion au broker MQTT {self.host}:{self.port}…")
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()  # IMPORTANT : loop_start pour laisser wait_for_start bloquer !

    def get_messages(self):
        return self.messages
    
    
class MQTTPublisher:
    def __init__(self, host="192.168.1.97", port=1883, topic="panic/game/rfid_memory/status"):
        self.host = host
        self.port = port
        self.topic = topic

        # Création du client MQTT
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect

    # ------------------ CALLBACKS ------------------
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code.is_failure:
            print(f"❌ Échec connexion : {reason_code}")
        else:
            print(f"✅ Connecté au broker {self.host}:{self.port}")

    # ------------------ MÉTHODES ------------------
    def start(self):
        """Connecte le client et lance la loop en arrière-plan"""
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def publish_state(self, session_id: str, state: str = "SUCCESS"):
        """Publie le JSON sur le topic"""
        payload = {
            "sessionId": session_id,
            "state": state
        }
        payload_str = json.dumps(payload)
        print(f"📤 Publication sur {self.topic} : {payload_str}")
        self.client.publish(self.topic, payload_str, qos=1)
