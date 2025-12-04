import os
import time
import json
import random

import paho.mqtt.client as mqtt

from led_controller import LedController
from button_controller import ButtonController

GAME_ID = "button-flash"


class MiniGameButtonFlash:
    def __init__(self, led: LedController, buttons: ButtonController):
        self.led = led
        self.buttons = buttons

        self.mqtt_host = os.getenv("MQTT_HOST", "10.4.1.47")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))

        # Param du nb de bonne reponse a donner pour reussir
        self.max_success = 20

        # Temps de réaction pour le player
        self.reaction_limit_ms = 800

        # Etat de la partie
        self.current_round = 0
        self.success_count = 0
        self.stop_requested = False
        self.active = False
        self.session_id: str | None = None

        # MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self.client.connect(self.mqtt_host, self.mqtt_port)
        self.client.loop_start()

        self.led.set_red_status_on()


    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with code {rc}")

        # Suscribe des annonces du serveur
        client.subscribe("panic/server/session", qos=1)

        # Suscribe pour mettre fin au minijeu
        client.subscribe(f"panic/game/{GAME_ID}/cmd", qos=1)

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip()
        print(f"[MQTT] Message on {msg.topic}: {payload}")

        # Annonce de session par le serveur
        if msg.topic == "panic/server/session":
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                print("[MQTT] Invalid JSON on panic/server/session")
                return

            games = data.get("games", [])
            session_id = data.get("sessionId")

            # Verif si minijeu select
            if GAME_ID in games and session_id is not None:
                print(f"[GAME] Selected for session {session_id}")
                self.session_id = session_id
                self.active = True
                self.stop_requested = False
                self.current_round = 0
                self.success_count = 0

                self.led.set_green_status_on()

        #
        #Commande pour le minieu
        elif msg.topic == f"panic/game/{GAME_ID}/cmd":
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                print("[MQTT] Invalid JSON on panic/game/{GAME_ID}/cmd")
                return

            cmd = data.get("cmd")
            sid = data.get("sessionId")

            if self.session_id is not None and sid is not None and sid != self.session_id:
                return

            if cmd == "STOP":
                print("[GAME] STOP received from server.")
                self.stop_requested = True

    # ---------- Publication du statut final ----------

    def _publish_final_status(self, success: bool):
        """
        Envoie le statut final attendu par ton serveur :
        topic: panic/game/button-flash/status
        """
        if not self.session_id:
            return

        payload = {
            "sessionId": self.session_id,
            "gameId": GAME_ID,
            "state": "SUCCESS",
            # "total_success": self.success_count,
            # "max_success": self.max_success,
            # "stopped_by_server": self.stop_requested,
        }
        topic = f"panic/game/{GAME_ID}/status"
        self.client.publish(topic, json.dumps(payload))
        print(f"[MQTT] Final status published on {topic}: {payload}")

    # ---------- Logique d'une manche ----------

    def play_one_round(self):
        if not self.active or self.stop_requested or not self.session_id:
            return

        self.current_round += 1
        round_id = self.current_round

        print(f"\n--- Round {round_id} ---")

        self.led.all_off()
        self.led.set_green_status_on()
        self.led.blink_all(cycles=1, speed=0.3)

        # Randomisation de la couleur et choix
        target = random.choice(["GREEN", "BLUE", "RED"])
        print("Target color:", target)

        start_time = time.time()
        pressed = None

        while not self.stop_requested:
            elapsed_ms = int((time.time() - start_time) * 1000)
            if elapsed_ms > self.reaction_limit_ms:
                break

            self.led.set(target, True)
            for _ in range(25):
                if self.stop_requested:
                    break

                pressed = self.buttons.check_pressed()
                if pressed is not None:
                    break

                elapsed_ms = int((time.time() - start_time) * 1000)
                if elapsed_ms > self.reaction_limit_ms:
                    break

                time.sleep(0.01)

            if pressed is not None or self.stop_requested:
                break

            self.led.set(target, False)
            for _ in range(25):
                if self.stop_requested:
                    break

                pressed = self.buttons.check_pressed()
                if pressed is not None:
                    break

                elapsed_ms = int((time.time() - start_time) * 1000)
                if elapsed_ms > self.reaction_limit_ms:
                    break

                time.sleep(0.01)

            if pressed is not None or self.stop_requested:
                break

        end_time = time.time()
        self.led.all_off()

        reaction_ms = int((end_time - start_time) * 1000)

        if pressed is None:
            print("No button pressed or too slow.")
        else:
            print("Pressed:", pressed)

        success = (
            not self.stop_requested
            and pressed is not None
            and pressed == target
            and reaction_ms <= self.reaction_limit_ms
        )

        if success:
            self.success_count += 1

        print(
            f"Success: {success}, reaction: {reaction_ms} ms, "
            f"total success: {self.success_count}/{self.max_success}"
        )

        # debug
        round_result = {
            "sessionId": self.session_id,
            "gameId": GAME_ID,
            "round": round_id,
            "expected": target,
            "pressed": pressed,
            "success": success,
            "reaction_ms": reaction_ms,
            "total_success": self.success_count,
        }
        self.client.publish(
            f"panic/game/{GAME_ID}/round",
            json.dumps(round_result)
        )

    # ---------- Boucle principale ----------

    def run(self):
        print("MiniGameButtonFlash running. Waiting for sessions from server...")
        try:
            while True:
                # session active => minijeu run.
                if (
                    self.active
                    and not self.stop_requested
                    and self.session_id is not None
                    and self.success_count < self.max_success
                ):
                    self.play_one_round()
                    time.sleep(0.2)

                    if self.success_count >= self.max_success:
                        print("[GAME] Game completed with enough successes.")
                        self._publish_final_status(True)

                        self.led.blink_status_green(duration=3.0, period=0.3)
                        self.led.set_red_status_on()

                        self.active = False
                        self.session_id = None
                        self.stop_requested = False

                # partie ENDGAME => STOP reçu depuis le serveur
                elif self.stop_requested and self.session_id is not None:
                    print("[GAME] Stopped by server, reporting FAIL.")
                    self._publish_final_status(False)

                    self.led.set_red_status_on()

                    self.active = False
                    self.session_id = None
                    self.stop_requested = False
                    self.success_count = 0
                    self.current_round = 0

                time.sleep(0.05)

        except KeyboardInterrupt:
            print("Interrupted by user.")
        finally:
            self.led.cleanup()
            self.client.loop_stop()
            self.client.disconnect()


if __name__ == "__main__":
    led = LedController()
    buttons = ButtonController()
    game = MiniGameButtonFlash(led, buttons)
    game.run()
