from RFIDreader import RFIDReader

isPlaying = True
reader = RFIDReader()

while isPlaying:
    
    dataFirstCard = reader.Read()
    
    dataSecondCard = reader.Read()
