import os
import time
import json
import random

import paho.mqtt.client as mqtt

from led_controller import LedController
from button_controller import ButtonController


class MiniGameButtonFlash:
    def __init__(self, led: LedController, buttons: ButtonController):
        self.led = led
        self.buttons = buttons

        self.mqtt_host = os.getenv("MQTT_HOST", "10.4.1.47")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))

        self.max_success = 5
        self.reaction_limit_ms = 2000

        self.current_round = 0
        self.success_count = 0
        self.stop_requested = False

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self.client.connect(self.mqtt_host, self.mqtt_port)
        self.client.loop_start()

    # MQTT callbacks

    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with code {rc}")
        client.subscribe("panic/game/stop")

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode().strip()
        print(f"[MQTT] Message on {msg.topic}: {payload}")

        if msg.topic == "panic/game/stop":
            self.stop_requested = True

    # Game logic

    def play_one_round(self):
        self.current_round += 1
        round_id = self.current_round

        print(f"\n--- Round {round_id} ---")

        # Intro blink
        self.led.all_off()
        self.led.blink_all(cycles=2, speed=0.4)

        # Choose target color
        target = random.choice(["GREEN", "BLUE", "RED"])
        print("Target color:", target)

        start_time = time.time()
        pressed = None

        # Loop until button press, timeout, or external stop
        while not self.stop_requested:
            elapsed_ms = int((time.time() - start_time) * 1000)
            if elapsed_ms > self.reaction_limit_ms:
                break

            # Blink target led on
            self.led.set(target, True)
            for _ in range(40):
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

            # Blink target led off
            self.led.set(target, False)
            for _ in range(40):
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

        result = {
            "round": round_id,
            "expected": target,
            "pressed": pressed,
            "success": success,
            "reaction_ms": reaction_ms,
            "total_success": self.success_count,
            "game_completed": self.success_count >= self.max_success,
            "stopped_by_server": self.stop_requested,
        }

        self.client.publish("panic/game/result", json.dumps(result))

    def run(self):
        print("MiniGameButtonFlash running. Ctrl+C to stop.")
        try:
            while (
                not self.stop_requested
                and self.success_count < self.max_success
            ):
                self.play_one_round()
                time.sleep(0.5)

            status = {
                "game_completed": self.success_count >= self.max_success,
                "total_success": self.success_count,
                "stopped_by_server": self.stop_requested,
            }

            self.client.publish("panic/game/status", json.dumps(status))
            print("Game finished:", status)

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
