from RFIDreader import RFIDReader
from screenLCD import ScreenLCD
from memory import Memory
from ledController import LedController
from mqtt import *

GameIsPlaying = True
reader = RFIDReader()
lcd = ScreenLCD() 
ledController = LedController()


def StartGame():
    memory = Memory(reader, lcd, ledController)
    memory.Play()   

def Main():
    while GameIsPlaying:
        mqttClient = MQTTClientWrapper()
        mqttClient.start()
        ledController.OnLightRed()
        mqttClient.wait_for_start()
        StartGame()
        mqttPublisher = MQTTPublisher()
        mqttPublisher.start()
        mqttPublisher.publish_state(mqttClient.sessionID)
        
Main()