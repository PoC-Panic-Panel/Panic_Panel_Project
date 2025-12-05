from RFIDreader import RFIDReader
from screenLCD import ScreenLCD
from memory import Memory
from ledController import LedController
from mqtt import MQTTWrapper

game_is_playing = True
reader = RFIDReader()
lcd = ScreenLCD() 
led_controller = LedController()
mqtt = MQTTWrapper()

def start_game():
    mqtt.start_event.clear()
    mqtt.stop_event.clear()                                                    
    memory = Memory(reader, lcd, led_controller, mqtt)
    memory.play()   

def main():
    mqtt.start()
    while game_is_playing:
        start_game()
        
main()