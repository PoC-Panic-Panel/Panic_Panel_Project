import RPi.GPIO as GPIO
from config import (
    PIN_LED_BROKER,
    PIN_LED_SERVICE,
    PIN_LED_EASY,
    PIN_LED_MEDIUM,
    PIN_LED_HARD,
    PIN_LED_START,
    PIN_BTN_EASY,
    PIN_BTN_MEDIUM,
    PIN_BTN_HARD,
    PIN_BTN_START,
    PIN_BTN_STOP,
)


class GpioManager:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # --- LEDs en sortie ---
        for pin in (
            PIN_LED_BROKER,
            PIN_LED_SERVICE,
            PIN_LED_EASY,
            PIN_LED_MEDIUM,
            PIN_LED_HARD,
            PIN_LED_START,
        ):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # --- Boutons  ---
        for pin in (
            PIN_BTN_EASY,
            PIN_BTN_MEDIUM,
            PIN_BTN_HARD,
            PIN_BTN_START,
            PIN_BTN_STOP,
        ):
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # ---------- LED ----------

    def set_service_led(self, on: bool):
        GPIO.output(PIN_LED_SERVICE, GPIO.HIGH if on else GPIO.LOW)

    def set_broker_led(self, on: bool):
        GPIO.output(PIN_LED_BROKER, GPIO.HIGH if on else GPIO.LOW)

    def set_difficulty_leds(self, difficulty: str):
        GPIO.output(PIN_LED_EASY, GPIO.HIGH if difficulty == "EASY" else GPIO.LOW)
        GPIO.output(PIN_LED_MEDIUM, GPIO.HIGH if difficulty == "MEDIUM" else GPIO.LOW)
        GPIO.output(PIN_LED_HARD, GPIO.HIGH if difficulty == "HARD" else GPIO.LOW)

    def set_start_led(self, on: bool):
        GPIO.output(PIN_LED_START, GPIO.HIGH if on else GPIO.LOW)

    # ---------- Boutons ----------

    def is_pressed(self, pin: int) -> bool:
        """Retourne True si le bouton donné (pin) est pressé (actif bas)."""
        return GPIO.input(pin) == GPIO.LOW

    def is_stop_pressed(self) -> bool:
        """Retourne True si le bouton STOP est pressé."""
        return GPIO.input(PIN_BTN_STOP) == GPIO.LOW

    # ---------- Nettoyage ----------

    def cleanup(self):
        GPIO.cleanup()
