from gpiozero import Button
import time
from ADCDevice import *

Z_Pin = 18
button = Button(Z_Pin)
adc = ADCDevice()

def setup():
    global adc
    if (adc.detectI2C(0x4b)):
        adc = ADS7830()
    else:
        print("No ADC device found, exiting...")
        exit(-1)

def loop():
    while True:
        val_Z = not button.value
        val_X = adc.analogRead(0)
        val_Y = adc.analogRead(1)
        print("Z: {}, X: {}, Y: {}".format(val_Z, val_X, val_Y))
        time.sleep(0.01)

def destroy():
    adc.close()
    button.close()

if __name__ == '__main__':
    print("Program is starting...")
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
        print("Ending program...")