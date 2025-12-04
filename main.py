import RPi.GPIO as GPIO
from ledcontroller import LEDController
from buzzercontroller import BuzzerController
from soundpanic import SoundPanic

GPIO.setmode(GPIO.BOARD)

def main():
    GPIO.setwarnings(False)
    
    led = LEDController(redled=36, yellowled=38, greenled=37)
    buzzer = BuzzerController(buzzer=32)
    game = SoundPanic(trig=16, echo=18, ledcontroller=led, buzzercontroller=buzzer)
    
    try:
        while True:
            game.start()
    except KeyboardInterrupt:
        buzzer.cleanup()
        GPIO.cleanup()

if __name__ == "__main__":
    main()