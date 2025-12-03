import time
import RPi.GPIO as GPIO


class LedController:
    LED_GREEN = 17
    LED_BLUE = 27
    LED_RED = 22

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.LED_GREEN, GPIO.OUT)
        GPIO.setup(self.LED_BLUE, GPIO.OUT)
        GPIO.setup(self.LED_RED, GPIO.OUT)

        self.all_off()

    def set(self, color: str, state: bool):
        pin = {
            "GREEN": self.LED_GREEN,
            "BLUE": self.LED_BLUE,
            "RED": self.LED_RED
        }.get(color)

        if pin is None:
            return

        GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)

    def all_off(self):
        GPIO.output(self.LED_GREEN, GPIO.LOW)
        GPIO.output(self.LED_BLUE, GPIO.LOW)
        GPIO.output(self.LED_RED, GPIO.LOW)

    def blink_all(self, cycles=3, speed=0.5):
        for _ in range(cycles):
            GPIO.output(self.LED_GREEN, GPIO.HIGH)
            GPIO.output(self.LED_BLUE, GPIO.HIGH)
            GPIO.output(self.LED_RED, GPIO.HIGH)
            time.sleep(speed)

            self.all_off()
            time.sleep(speed)

    def cleanup(self):
        self.all_off()
        GPIO.cleanup()
