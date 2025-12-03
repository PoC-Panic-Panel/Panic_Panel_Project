# main.py
import time
import uuid
from typing import Optional



from config import (
    DIFFICULTY_SETTINGS,
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
            time.sleep(0.3)  # évite plusieurs lancements si on garde le bouton appuyé

    def start_new_session(self):
        settings = DIFFICULTY_SETTINGS[self.current_difficulty]

        self.current_session = GameSession(
            difficulty=self.current_difficulty,
            total_games=settings["games_count"],
            time_limit=settings["time_limit"],
        )
        self.current_session_id = f"S-{uuid.uuid4().hex[:8]}"

        # LED bleue ON pendant la partie
        self.gpio.set_start_led(True)

        # Affichage initial
        self.display.show_session(self.current_session)


        from config import DIFFICULTY_GAMES #Ne pas oublier de le virer
        games_to_run = DIFFICULTY_GAMES[self.current_difficulty]
        
        # Notifier les mini-jeux (s'ils écoutent ce topic)
        payload = {
            "sessionId": self.current_session_id,
            "difficulty": self.current_difficulty,
            "games": games_to_run,
            "gamesCount": settings["games_count"],
            "timeLimit": settings["time_limit"],
        }
        self.mqtt.publish(TOPIC_SESSION_NEW, payload)

    # ---------- Boucle principale ----------

    def loop(self):
        try:
            while True:
                if self.current_session is None:
                    # Mode attente : gestion des boutons de difficulté + start
                    self._handle_buttons_idle()
                else:
                    # Partie en cours : mise à jour écran et gestion fin
                    self.display.show_session(self.current_session)

                    if self.current_session.is_finished():
                        # Fin de partie
                        self.display.show_result(self.current_session)
                        self.gpio.set_start_led(False)

                        # Reset
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
