from RPLCD import *
from time import sleep
import threading
import time
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import random

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
lcd = CharLCD('PCF8574', 0x27)

UP_btn_PIN = 25
DOWN_btn_PIN = 24
CONFIRM_btn_PIN = 18
LEFT_btn_PIN = 12
RIGHT_btn_PIN = 20
Buzzer_PIN = 16

UP_btn = GPIO.setup(UP_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
DOWN_btn = GPIO.setup(DOWN_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
CONFIRM_btn = GPIO.setup(CONFIRM_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
LEFT_btn = GPIO.setup(LEFT_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
RIGHT_btn = GPIO.setup(RIGHT_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Buzzer_PIN, GPIO.OUT)
Buzzer = GPIO.PWM(Buzzer_PIN,1000)

try:
    unlockCode = [0,0,0,0]
    passcode = [0,0,0,0]
    lcd.cursor_pos = (0, 0)
    currentDigit = 0

    mutex = threading.Lock()

    def GenerateUnlockCode():
        global unlockCode
        for i in range(4):
            unlockCode[i] = random.randint(0, 9)

    def showPasscode(passcode) :
        display = "#    "
        for digit in passcode:
            display += str(digit) + " "
        return display

    def ChangeCurrentDigit(value):
        global currentDigit
        if value == 'left':
            if currentDigit == 0:
                currentDigit = 3
            else:
                currentDigit = currentDigit - 1
        elif value == 'right':
            if currentDigit == 3:
                currentDigit = 0
            else:
                currentDigit = currentDigit + 1
        mutex.acquire()
        lcd.clear()
        lcd.write_string(showPasscode(passcode))
        mutex.release()

    def ChangeCurrentValue(value):
        global passcode
        if value == 'up':
            if passcode[currentDigit] == 9:
                passcode[currentDigit] = 0
            else:
                passcode[currentDigit] = passcode[currentDigit] + 1
        elif value == 'down':
            if passcode[currentDigit] == 0:
                passcode[currentDigit] = 9
            else:
                passcode[currentDigit] = passcode[currentDigit] - 1
        mutex.acquire()
        lcd.clear()
        lcd.write_string(showPasscode(passcode))
        mutex.release()


    def numberValueChange():
        while True:
            etat_UP_button = GPIO.input(UP_btn_PIN)
            etat_Down_button = GPIO.input(DOWN_btn_PIN)
            etat_Confirm_button = GPIO.input(CONFIRM_btn_PIN)
            etat_Left_button = GPIO.input(LEFT_btn_PIN)
            etat_Right_button = GPIO.input(RIGHT_btn_PIN)
            if etat_Left_button == GPIO.HIGH:
                ChangeCurrentDigit('left')
                sleep(0.3)
            elif etat_Right_button == GPIO.HIGH:
                ChangeCurrentDigit('right')
                sleep(0.3)
            elif etat_UP_button == GPIO.HIGH:
                ChangeCurrentValue('up')
                sleep(0.3)
            elif etat_Down_button == GPIO.HIGH:
                ChangeCurrentValue('down')
                sleep(0.3)
            elif CONFIRM_btn == GPIO.HIGH:
                if passcode == unlockCode:
                    mutex.acquire()
                    lcd.clear()
                    lcd.write_string("Unlocked!")
                    mutex.release()
                    Buzzer.start(100)
                    time.sleep(1)
                    Buzzer.stop()
                    sleep(2)
                    GenerateUnlockCode()
                    mutex.acquire()

                else:
                    mutex.acquire()
                    lcd.cursor_pos = (1, 0)
                    lcd.write_string("Wrong Code!")
                    mutex.release()
                    sleep(2)
                    mutex.acquire()
                    lcd.cursor_pos = (1, 0)
                    lcd.write_string(" " * 16)
                    mutex.release()
                sleep(0.3)

    def blinkingCurrentValue():
        global currentDigit
        while True:
            mutex.acquire()
            lcd.cursor_pos = (0, 5 + currentDigit * 2)
            lcd.write_string(" ")
            mutex.release()
            sleep(0.5)
            mutex.acquire()
            lcd.cursor_pos = (0, 5 + currentDigit * 2)
            lcd.write_string(str(passcode[currentDigit]))
            mutex.release()
            sleep(0.5)


    def buzzerMorseCode():
        morse_code_dict = {
            '0': '-----',
            '1': '.----',
            '2': '..---',
            '3': '...--',
            '4': '....-',
            '5': '.....',
            '6': '-....',
            '7': '--...',
            '8': '---..',
            '9': '----.'
        }
        print(unlockCode)
        code = ''.join(map(str, unlockCode))
        while True:
            mutex.acquire()
            lcd.cursor_pos = (1, 5)
            lcd.write_string("Listen!")
            mutex.release()
            for digit in code:
                morse_code = morse_code_dict[digit]
                for symbol in morse_code:
                    if symbol == '.':
                        Buzzer.start(50)
                        time.sleep(0.2)
                        Buzzer.stop()
                        time.sleep(0.2)
                    elif symbol == '-':
                        Buzzer.start(50)
                        time.sleep(0.8)
                        GPIO.output(Buzzer_PIN, GPIO.LOW)
                        Buzzer.stop()
                        time.sleep(0.2)
                time.sleep(1.0)
            mutex.acquire()
            lcd.cursor_pos = (1, 0)
            lcd.write_string(" " * 16)
            mutex.release()
            time.sleep(5)

    GenerateUnlockCode()
    lcd.clear()
    lcd.write_string(showPasscode(passcode))

    thread_numberValueChange = threading.Thread(target=numberValueChange)
    thread_blinkingCurrentValue = threading.Thread(target=blinkingCurrentValue)
    thread_buzzerMorseCode = threading.Thread(target=buzzerMorseCode)

    thread_numberValueChange.start()
    thread_blinkingCurrentValue.start()
    thread_buzzerMorseCode.start()
    thread_numberValueChange.join()
    thread_blinkingCurrentValue.join()
    thread_buzzerMorseCode.join()

except KeyboardInterrupt:
    lcd.clear()
    GPIO.cleanup()
    thread_blinkingCurrentValue.running = False
    thread_numberValueChange.running = False
    thread_buzzerMorseCode.running = False