from RPLCD import *
from time import sleep
import threading
import time
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
import random
from MQTTClient import MQTTWrapper

# ----- Component's Pin ----- #

up_btn_PIN = 22
down_btn_PIN = 20
confirm_btn_PIN = 12
left_btn_PIN = 19
right_btn_PIN = 26
buzzer_PIN = 16
green_LED_PIN = 23
red_LED_PIN = 25


# ---- Component's GPIO Setup ----- #

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
lcd = CharLCD('PCF8574', 0x27)
up_btn = GPIO.setup(up_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
down_btn = GPIO.setup(down_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
confirm_btn = GPIO.setup(confirm_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
left_btn = GPIO.setup(left_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
right_btn = GPIO.setup(right_btn_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(buzzer_PIN, GPIO.OUT)
buzzer = GPIO.PWM(buzzer_PIN,1000)
greenLED = GPIO.setup(green_LED_PIN, GPIO.OUT)
redLED = GPIO.setup(red_LED_PIN, GPIO.OUT)


# ----- Global Variables ----- #

gameUnlocked = False
unlockCode = [0,0,0,0]
passcode = [0,0,0,0]
lcd.cursor_pos = (0, 0)
currentDigit = 0
mutex = threading.Lock()

# ----- Main Code ----- #
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

def EndGame():
    global gameUnlocked
    gameUnlocked = True
    GPIO.output(green_LED_PIN, GPIO.HIGH)
    GPIO.output(red_LED_PIN, GPIO.LOW)

def numberValueChange():
    while gameUnlocked == False and mqttWrapper.stop_event.is_set() == False:
        etat_up_button = GPIO.input(up_btn_PIN)
        etat_down_button = GPIO.input(down_btn_PIN)
        etat_confirm_button = GPIO.input(confirm_btn_PIN)
        etat_left_button = GPIO.input(left_btn_PIN)
        etat_right_button = GPIO.input(right_btn_PIN)
        if etat_left_button == GPIO.HIGH:
            ChangeCurrentDigit('left')
            sleep(0.3)
        elif etat_right_button == GPIO.HIGH:
            ChangeCurrentDigit('right')
            sleep(0.3)
        elif etat_up_button == GPIO.HIGH:
            ChangeCurrentValue('up')
            sleep(0.3)
        elif etat_down_button == GPIO.HIGH:
            ChangeCurrentValue('down')
            sleep(0.3)
        elif etat_confirm_button == GPIO.HIGH:
            if passcode == unlockCode:
                EndGame()
                break
            else:
                mutex.acquire()
                lcd.cursor_pos = (1, 2)
                lcd.write_string("Wrong Code!")
                mutex.release()
                sleep(1.5)
                mutex.acquire()
                lcd.cursor_pos = (1, 0)
                lcd.write_string(" " * 16)
                mutex.release()
                sleep(0.3)

def blinkingCurrentValue():
    global currentDigit
    try:
        while gameUnlocked == False and mqttWrapper.stop_event.is_set() == False:
            mutex.acquire()
            lcd.cursor_pos = (0, 5 + currentDigit * 2)
            lcd.write_string(" ")
            mutex.release()
            if gameUnlocked or mqttWrapper.stop_event.is_set():
                break
            sleep(0.5)
            mutex.acquire()
            lcd.cursor_pos = (0, 5 + currentDigit * 2)
            lcd.write_string(str(passcode[currentDigit]))
            mutex.release()
            if gameUnlocked or mqttWrapper.stop_event.is_set():
                break
            sleep(0.5)
    except Exception as e:
        print("Error in blinkingCurrentValue:", e)


def buzzerMorseCode():
    try:
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
        while gameUnlocked == False and mqttWrapper.stop_event.is_set() == False:
            for digit in code:
                if gameUnlocked:
                    break
                mutex.acquire()
                lcd.cursor_pos = (1, 5)
                lcd.write_string("Listen!")
                mutex.release()
                morse_code = morse_code_dict[digit]
                for symbol in morse_code:
                    if gameUnlocked or mqttWrapper.stop_event.is_set():
                        break
                    if symbol == '.':
                        buzzer.start(50)
                        time.sleep(0.2)
                        buzzer.stop()
                        time.sleep(0.2)
                    elif symbol == '-':
                        buzzer.start(50)
                        time.sleep(0.8)
                        GPIO.output(buzzer_PIN, GPIO.LOW)
                        buzzer.stop()
                        time.sleep(0.2)
                if gameUnlocked or mqttWrapper.stop_event.is_set():
                    break
                time.sleep(1.0)
            mutex.acquire()
            lcd.cursor_pos = (1, 0)
            lcd.write_string(" " * 16)
            mutex.release()
            if gameUnlocked or mqttWrapper.stop_event.is_set():
                break
            time.sleep(5)
    except Exception as e:
        print("Error in buzzerMorseCode:", e)

def StartGame(): 
    try:
        global passcode 
        global gameUnlocked
        global currentDigit

        GPIO.output(red_LED_PIN, GPIO.LOW)
        GPIO.output(green_LED_PIN, GPIO.HIGH)
        passcode = [0,0,0,0]
        gameUnlocked = False
        currentDigit = 0
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
        thread_blinkingCurrentValue.running = False
        thread_numberValueChange.running = False
        thread_buzzerMorseCode.running = False
        GPIO.cleanup()
        lcd.clear()
        print("Program stopped by User")
    except Exception as e:
        print("An error occurred:", e)

def BlinkGreenLED():
    GPIO.output(green_LED_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(green_LED_PIN, GPIO.LOW)
    time.sleep(0.5)

try:         
    while True:
        GPIO.output(green_LED_PIN, GPIO.LOW)
        GPIO.output(red_LED_PIN, GPIO.HIGH)
        mqttWrapper = MQTTWrapper()
        mqttWrapper.start()
        mqttWrapper.wait_for_start()
        gameUnlocked = False
        StartGame()
        if gameUnlocked:
            mqttWrapper.publish_state("SUCCESS")
            lcd.clear()
            lcd.cursor_pos = (0, 3)
            lcd.write_string("Unlocked!")
            buzzer.start(100)
            sleep(1)
            buzzer.stop()
            while not mqttWrapper.stop_event.is_set():
                BlinkGreenLED()
        else:
            mqttWrapper.publish_state("FAILURE")
except Exception as e:
        print(f"Erreur dans la boucle principale : {e}")
