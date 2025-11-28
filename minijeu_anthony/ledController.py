import RPi.GPIO as GPIO

GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

class LedController:
    def __init__(self):
        pass
    
    def OnLightRed(self):
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        
    def OnLightGreen(self):
        GPIO.output(27, GPIO.LOW)
        GPIO.output(17, GPIO.HIGH)