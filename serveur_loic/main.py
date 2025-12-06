# main.py
import time
import uuid
import random
from typing import Optional



from config import (
    DIFFICULTY_SETTINGS,
    ALL_GAMES,
    PIN_BTN_EASY,
    PIN_BTN_MEDIUM,
    PIN_BTN_HARD,
    PIN_BTN_START,
    TOPIC_SESSION_NEW,
)

from game_session import GameSession, SessionState
from display import DisplayManager
from gpio_controls import GpioManager
from mqtt_client import MqttClient


class PanicServer:
    def __init__(self):
        self.display = DisplayManager()
        self.gpio = GpioManager()

        self.current_difficulty: str = "EASY"
        self.current_session: Optional[GameSession] = None
        self.current_session_id: Optional[str] = None
        self.current_games: list[str] = []

        # MQTT
        self.mqtt = MqttClient(
            on_game_status=self.on_game_status,
            on_connect_change=self.on_connect_change,
        )
        self.mqtt.start()

        # LEDs initiales
        self.gpio.set_difficulty_leds(self.current_difficulty)
        self.gpio.set_start_led(False)

        self.display.show_idle(self.current_difficulty)

    # ---------- Callbacks MQTT ----------

    def on_connect_change(self, connected: bool):
        self.gpio.set_broker_led(connected)
        # On montre un petit écran de statut rapide
        self.display.show_broker_status(connected)
        # Puis retour à l'écran normal
        if self.current_session is None:
            self.display.show_idle(self.current_difficulty)
        else:
            self.display.show_session(self.current_session)

    def on_game_status(self, session_id: str, success: bool):
        # On ignore les messages qui ne concernent pas la session en cours
        if self.current_session_id is None or session_id != self.current_session_id:
            return
        if self.current_session is None:
            return

        self.current_session.register_game_result(success)

    # ---------- Gestion des boutons en mode "idle" ----------

    def _handle_buttons_idle(self):
        # Petite tempo anti-rebond très simple
        if self.gpio.is_pressed(PIN_BTN_EASY):
            self.current_difficulty = "EASY"
            self.gpio.set_difficulty_leds(self.current_difficulty)
            self.display.show_idle(self.current_difficulty)
            time.sleep(0.2)

        elif self.gpio.is_pressed(PIN_BTN_MEDIUM):
            self.current_difficulty = "MEDIUM"
            self.gpio.set_difficulty_leds(self.current_difficulty)
            self.display.show_idle(self.current_difficulty)
            time.sleep(0.2)

        elif self.gpio.is_pressed(PIN_BTN_HARD):
            self.current_difficulty = "HARD"
            self.gpio.set_difficulty_leds(self.current_difficulty)
            self.display.show_idle(self.current_difficulty)
            time.sleep(0.2)

        # Démarrage de partie
        if self.gpio.is_pressed(PIN_BTN_START):
            self.start_new_session()
            time.sleep(0.3)

    def start_new_session(self):
        settings = DIFFICULTY_SETTINGS[self.current_difficulty]

        games_count = settings["games_count"]
        pool = list(ALL_GAMES)
        
        if games_count > len(pool):
            print(f"[WARN] game_count ({games_count}) > nb de mini-jeux ({len(pool)}), ajustement.")
            games_count = len(pool)
            
        games_to_run = random.sample(pool, games_count)
        self.current_games = games_to_run

        self.current_session = GameSession(
            difficulty=self.current_difficulty,
            total_games=games_count,
            time_limit=settings["time_limit"],
        )
        self.current_session_id = f"S-{uuid.uuid4().hex[:8]}"

        self.gpio.set_start_led(True)

        self.display.show_session(self.current_session)
        
        payload = {
            "sessionId": self.current_session_id,
            "difficulty": self.current_difficulty,
            "games": games_to_run,
            "gamesCount": games_count,
            "timeLimit": settings["time_limit"],
        }
        self.mqtt.publish(TOPIC_SESSION_NEW, payload)


    def loop(self):
        try:
            while True:
                if self.current_session is None:
                    self._handle_buttons_idle()
                else:
                    self.display.show_session(self.current_session)

                    if self.current_session.is_finished():
                        if self.current_session_id is not None and self.current_games:
                            stop_payload = {
                                "sessionId" : self.current_session_id,
                                "cmd": "STOP",
                                "reason": "TIMEOUT"
                            }
                            for game_id in self.current_games:
                                topic = f"panic/game/{game_id}/cmd"
                                self.mqtt.publish(topic, stop_payload)
                                
                        self.display.show_result(self.current_session)
                        self.gpio.set_start_led(False)

                        self.current_session = None
                        self.current_session_id = None
                        self.display.show_idle(self.current_difficulty)

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Arrêt demandé par l'utilisateur.")
        finally:
            self.mqtt.stop()
            self.gpio.cleanup()


if __name__ == "__main__":
    server = PanicServer()
    server.loop()
