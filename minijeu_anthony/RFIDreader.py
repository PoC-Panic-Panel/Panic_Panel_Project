from pirc522 import RFID

class RFIDReader:
    def __init__(self):
        self.rdr = RFID()
        self.util = self.rdr.util()
    
    def Read(self):
        self.rdr.wait_for_tag()
        
        (error, data) = self.rdr.request()
    
        (error, uid) = self.rdr.anticoll()
        if not error:
           uuid = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
           return uuid


            
