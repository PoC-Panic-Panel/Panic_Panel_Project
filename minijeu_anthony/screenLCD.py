from RPLCD.i2c import CharLCD
class ScreenLCD:
    def __init__(self):
        self.lcd = CharLCD("PCF8574", 0x27, port=1, cols=16, rows=2)
        
    def show(self,text):
        self.lcd.clear()
        self.lcd.write_string(text)
        
    def clear(self):
        self.lcd.clear()