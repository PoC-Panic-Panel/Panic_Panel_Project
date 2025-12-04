import json
import threading
import paho.mqtt.client as mqtt

class MQTTWrapper:
    def __init__(self, host="10.4.1.47", port=1883):
        self.host = host
        self.port = port
        self.sessionID = ""
        self.gameName = "rfid-memory"
        self.topicGame = "panic/server/session"
        self.topicTime = "panic/game/rfid-memory/cmd"
        self.statusTopic = "panic/game/rfid-memory/status"

        # MQTT client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        self.start_event = threading.Event()
        self.stop_event = threading.Event() 

        # Callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe

    # ------------------ CALLBACKS ------------------

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Échec connexion : {reason_code}.")
        else:
            print("Connecté, abonnement…")
            client.subscribe(self.topicGame, qos=1)
            client.subscribe(self.topicTime, qos=1)

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print(f"Abonnement rejeté : {reason_code_list[0]}")
        else:
            print(f"Abonnement réussi, QoS = {reason_code_list[0].value}")

    def on_message(self, client, userdata, message):
        try:
            text = message.payload.decode("utf-8")
            
            if message.topic == self.topicGame:
                print(message.topic)
                self.verify_game_start(text)
                
            if message.topic == self.topicTime:
                self.game_end(text)
        
        except Exception as e:
            print(f"Erreur dans on_message : {e}")
            
            
    def verify_game_start(self, text):
        payload = json.loads(text)

        if "games" not in payload:
            print("Le JSON ne contient pas 'games'")
            return
            
        self.sessionID = payload["sessionId"]

        games = payload["games"]

        if self.gameName in games:
            print("La partie commence")
            self.start_event.set()
            
    def game_end(self, text):
        payload = json.loads(text)
        
        cmd = payload["cmd"]
        
        sessionID = payload["sessionId"]
        
        if(sessionID == self.sessionID and cmd == "STOP"):
            self.stop_event.set()


    # ------------------ MÉTHODE BLOQUANTE ------------------

    def wait_for_start(self, timeout=None) -> bool:
        self.start_event.clear()
        self.stop_event.clear()
        print("En attente du message START…")
        received = self.start_event.wait(timeout=timeout)
        return received
    
    def publish_state(self, state: str = "SUCCESS"):
        payload = {
            "sessionId": self.sessionID,
            "state": state
        }
        payload_str = json.dumps(payload)
        print(f"Publication sur {self.statusTopic} : {payload_str}")
        self.client.publish(self.statusTopic, payload_str, qos=1)

    # ------------------ MQTT CONTROL ------------------

    def start(self):
        print(f"Connexion au broker MQTT {self.host}:{self.port}…")
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()