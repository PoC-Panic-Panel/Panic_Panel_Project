import time
import RPi.GPIO as GPIO


class LedController:
    LED_GREEN = 17
    LED_BLUE = 27
    LED_RED = 22

    LED_STATUS_GREEN = 23
    LED_STATUS_RED = 24

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.LED_GREEN, GPIO.OUT)
        GPIO.setup(self.LED_BLUE, GPIO.OUT)
        GPIO.setup(self.LED_RED, GPIO.OUT)

        GPIO.setup(self.LED_STATUS_GREEN, GPIO.OUT)
        GPIO.setup(self.LED_STATUS_RED, GPIO.OUT)

        self.all_off()
        self.set_red_status_on()

    # ----- LEDs de jeu -----

    def set(self, color: str, state: bool):
        pin = {
            "GREEN": self.LED_GREEN,
            "BLUE": self.LED_BLUE,
            "RED": self.LED_RED,
        }.get(color)

        if pin is None:
            return

        GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

    def all_off(self):
        GPIO.output(self.LED_GREEN, GPIO.LOW)
        GPIO.output(self.LED_BLUE, GPIO.LOW)
        GPIO.output(self.LED_RED, GPIO.LOW)

        # GPIO.output(self.LED_STATUS_GREEN, GPIO.LOW)
        # GPIO.output(self.LED_STATUS_RED, GPIO.LOW)

    def blink_all(self, cycles=3, speed=0.5):
        for _ in range(cycles):
            GPIO.output(self.LED_GREEN, GPIO.HIGH)
            GPIO.output(self.LED_BLUE, GPIO.HIGH)
            GPIO.output(self.LED_RED, GPIO.HIGH)
            time.sleep(speed)

            self.all_off()
            time.sleep(speed)

    # ----- LEDs de statut -----

    def set_green_status_on(self):
        GPIO.output(self.LED_STATUS_GREEN, GPIO.HIGH)
        GPIO.output(self.LED_STATUS_RED, GPIO.LOW)

    def set_red_status_on(self):
        GPIO.output(self.LED_STATUS_RED, GPIO.HIGH)
        GPIO.output(self.LED_STATUS_GREEN, GPIO.LOW)

    # def set_status_active(self, active: bool):
    #     """
    #     active = True  => LED verte ON, LED rouge OFF
    #     active = False => LED verte OFF, LED rouge ON
    #     """
    #     GPIO.output(self.LED_STATUS_GREEN, GPIO.HIGH if active else GPIO.LOW)
    #     GPIO.output(self.LED_STATUS_RED, GPIO.LOW if active else GPIO.HIGH)

    def blink_status_green(self, duration: float = 3.0, period: float = 0.3):
        """
        Fait clignoter la LED verte de statut pendant `duration` secondes,
        sans allumer la LED rouge.
        """
        end = time.time() + duration
        while time.time() < end:
            GPIO.output(self.LED_STATUS_GREEN, GPIO.HIGH)
            GPIO.output(self.LED_STATUS_RED, GPIO.LOW)
            time.sleep(period / 2)

            GPIO.output(self.LED_STATUS_GREEN, GPIO.LOW)
            time.sleep(period / 2)

    def cleanup(self):
        self.all_off()
        GPIO.cleanup()