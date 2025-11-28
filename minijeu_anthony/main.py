from RFIDreader import RFIDReader
from screenLCD import ScreenLCD
from memory import Memory

GameIsPlaying = True
reader = RFIDReader()
lcd = ScreenLCD() 

def StartGame():
    memory = Memory(reader, lcd)
    memory.Play()   

def Main():
    while GameIsPlaying:
        StartGame()
        
Main()