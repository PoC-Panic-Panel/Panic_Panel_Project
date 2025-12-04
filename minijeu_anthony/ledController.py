import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

class LedController:
    def __init__(self):
        pass
    
    def light_red_on(self):
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.HIGH)
        
    def light_green_on(self):
        GPIO.output(13, GPIO.LOW)
        GPIO.output(11, GPIO.HIGH)