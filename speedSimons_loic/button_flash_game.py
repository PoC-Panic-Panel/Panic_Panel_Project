import os
import time
import json
import random
import threading

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO


class ButtonFlashGame:
    def __init__(self):
        # GPIO (BCM)
        self.LED_GREEN = 17
        self.LED_BLUE = 27
        self.LED_RED = 22

        self.BTN_GREEN = 5
        self.BTN_BLUE = 6
        self.BTN_RED = 13

        # MQTT
        self.mqtt_host = os.getenv("MQTT_HOST", "192.168.1.97")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))

        # Mapping
        self.led_pins = {
            "GREEN": self.LED_GREEN,
            "BLUE": self.LED_BLUE,
            "RED": self.LED_RED,
        }

        self.btn_pins = {
            "GREEN": self.BTN_GREEN,
            "BLUE": self.BTN_BLUE,
            "RED": self.BTN_RED,
        }

        self.round_number = 0
        self._lock = threading.Lock()

        self._setup_gpio()
        self._setup_mqtt()

    # --- Setup ---

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.LED_GREEN, GPIO.OUT)
        GPIO.setup(self.LED_BLUE, GPIO.OUT)
        GPIO.setup(self.LED_RED, GPIO.OUT)

        GPIO.setup(self.BTN_GREEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN_BLUE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN_RED, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._all_leds_off()

    def _setup_mqtt(self):
        self.client = mqtt.Client()
        self.client.connect(self.mqtt_host, self.mqtt_port)
        self.client.loop_start()

    # --- Utilitaires LEDs / boutons ---

    def _all_leds_off(self):
        GPIO.output(self.LED_GREEN, GPIO.LOW)
        GPIO.output(self.LED_BLUE, GPIO.LOW)
        GPIO.output(self.LED_RED, GPIO.LOW)

    def _intro_blink_all(self, cycles=4, period=0.6):
        """
        Clignote toutes les LEDs en même temps
        cycles fois, à vitesse lente.
        """
        for _ in range(cycles):
            GPIO.output(self.LED_GREEN, GPIO.HIGH)
            GPIO.output(self.LED_BLUE, GPIO.HIGH)
            GPIO.output(self.LED_RED, GPIO.HIGH)
            time.sleep(period)

            self._all_leds_off()
            time.sleep(period)

    def _wait_for_any_button(self):
        """
        Attend qu'un des 3 boutons soit pressé.
        Retourne la couleur correspondante.
        """
        while True:
            if GPIO.input(self.BTN_GREEN) == 0:
                return "GREEN"
            if GPIO.input(self.BTN_BLUE) == 0:
                return "BLUE"
            if GPIO.input(self.BTN_RED) == 0:
                return "RED"
            time.sleep(0.01)

    # --- Logique d'une manche ---

    def _play_one_round(self):
        with self._lock:
            self.round_number += 1
            round_id = self.round_number

        print(f"\n--- Round {round_id} ---")

        # 1) Intro : toutes les LEDs clignotent
        self._all_leds_off()
        self._intro_blink_all()

        # 2) Choix de la couleur cible localement (pas besoin du serveur)
        target_color = random.choice(["GREEN", "BLUE", "RED"])
        target_led = self.led_pins[target_color]

        print(f"Couleur cible : {target_color}")

        # 3) Clignotement lent de la LED cible + attente du bon bouton
        self._all_leds_off()
        start_time = time.time()
        pressed_color = None

        # On clignote tant que le joueur n'a pas appuyé
        while pressed_color is None:
            GPIO.output(target_led, GPIO.HIGH)
            # Pendant que la LED est ON, on check le bouton
            for _ in range(50):  # 50 x 10 ms = 0.5 s
                if GPIO.input(self.BTN_GREEN) == 0:
                    pressed_color = "GREEN"
                    break
                if GPIO.input(self.BTN_BLUE) == 0:
                    pressed_color = "BLUE"
                    break
                if GPIO.input(self.BTN_RED) == 0:
                    pressed_color = "RED"
                    break
                time.sleep(0.01)
            if pressed_color is not None:
                break

            GPIO.output(target_led, GPIO.LOW)
            # LED OFF, on continue à checker
            for _ in range(50):
                if GPIO.input(self.BTN_GREEN) == 0:
                    pressed_color = "GREEN"
                    break
                if GPIO.input(self.BTN_BLUE) == 0:
                    pressed_color = "BLUE"
                    break
                if GPIO.input(self.BTN_RED) == 0:
                    pressed_color = "RED"
                    break
                time.sleep(0.01)

        end_time = time.time()
        self._all_leds_off()

        reaction_ms = int((end_time - start_time) * 1000)
        success = (pressed_color == target_color)

        print(f"Bouton pressé : {pressed_color}, succès = {success}, temps = {reaction_ms} ms")

        result = {
            "round": round_id,
            "expected": target_color,
            "pressed": pressed_color,
            "success": success,
            "reaction_ms": reaction_ms,
        }

        # 4) Envoi du résultat au serveur MQTT
        self.client.publish("panic/game/result", json.dumps(result))
        print("Résultat envoyé sur panic/game/result")

    # --- Boucle principale ---

    def run_forever(self):
        print("ButtonFlashGame en cours. Ctrl+C pour arrêter.")
        try:
            while True:
                self._play_one_round()
                time.sleep(1.0)  # petite pause entre les manches
        except KeyboardInterrupt:
            print("\nInterruption par l'utilisateur.")
        finally:
            self._cleanup()

    def _cleanup(self):
        self._all_leds_off()
        GPIO.cleanup()
        self.client.loop_stop()
        self.client.disconnect()
        print("Arrêt propre.")


if __name__ == "__main__":
    game = ButtonFlashGame()
    game.run_forever()
