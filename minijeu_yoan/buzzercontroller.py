import RPi.GPIO as GPIO

class BuzzerController:
    def __init__(self, buzzer):
        GPIO.setup(buzzer, GPIO.OUT)
        self.BUZZER = GPIO.PWM(buzzer, 440)
        self.BUZZER.start(0)
    
    def play(self, frequency, duty_cycle=50):
        self.BUZZER.ChangeFrequency(frequency)
        self.BUZZER.ChangeDutyCycle(duty_cycle)
    
    def stop(self):
        self.BUZZER.ChangeDutyCycle(0)
    
    def cleanup(self):
        self.BUZZER.stop()