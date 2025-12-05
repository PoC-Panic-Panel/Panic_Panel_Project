import RPi.GPIO as GPIO

class LEDController:
    def __init__(self, redled, yellowled, greenled):
        self.REDLED = redled
        self.YELLOWLED = yellowled
        self.GREENLED = greenled
        
        GPIO.setup(self.REDLED, GPIO.OUT)
        GPIO.setup(self.YELLOWLED, GPIO.OUT)
        GPIO.setup(self.GREENLED, GPIO.OUT)
        
        GPIO.output(self.REDLED, True)
        GPIO.output(self.GREENLED, False)
        GPIO.output(self.YELLOWLED, False)
    
    def set_red(self, state):
        GPIO.output(self.REDLED, state)
    
    def set_yellow(self, state):
        GPIO.output(self.YELLOWLED, state)
    
    def set_green(self, state):
        GPIO.output(self.GREENLED, state)
    
    def toggle_green(self):
        current = GPIO.input(self.GREENLED)
        GPIO.output(self.GREENLED, not current)
    
    def toggle_yellow(self):
        current = GPIO.input(self.YELLOWLED)
        GPIO.output(self.YELLOWLED, not current)
    
    def reset(self):
        self.set_red(True)
        self.set_yellow(False)
        self.set_green(False)