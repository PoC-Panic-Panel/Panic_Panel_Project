import RPi.GPIO as GPIO


class ButtonController:
    BTN_GREEN = 5
    BTN_BLUE = 6
    BTN_RED = 13

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.BTN_GREEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN_BLUE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BTN_RED, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def check_pressed(self) -> str | None:
        if GPIO.input(self.BTN_GREEN) == 0:
            return "GREEN"
        if GPIO.input(self.BTN_BLUE) == 0:
            return "BLUE"
        if GPIO.input(self.BTN_RED) == 0:
            return "RED"
        return None
