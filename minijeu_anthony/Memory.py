import time
class Memory:
    def __init__(self, reader, verifier, lcd):
        self.reader = reader
        self.verifier = verifier
        self.lcd = lcd
        
        
    def __AskCard(self):
        CardIsGood = False
        while CardIsGood != True:
            self.lcd.Show("Faite passer une carte")
            uuidCard = self.reader.Read()
            if(self.verifier.IsACardInTheGame(uuidCard)):
                value = self.verifier.GetValue(uuidCard)
                self.lcd.Show(value)
                CardIsGood = True
            else:
                self.lcd.Show("Erreur de lecture")
                time.sleep(1)
                
        return uuidCard      

    def __CheckPair(self, uuidFirstCard, uuidSecondCard):
        if(self.verifier.IsSameCard(uuidFirstCard, uuidSecondCard)):
            self.lcd.Show("Meme carte")
        elif(self.verifier.IsAPairFound(uuidFirstCard, uuidSecondCard)):
            self.lcd.Show("Pair deja trouvee")
        else:
            if(self.verifier.IsAPair(uuidFirstCard, uuidSecondCard)):
                self.lcd.Show("C'est une pair!")
                nbOfPairPlayerFound = nbOfPairPlayerFound + 1
            else:
                self.lcd.Show("Nan nan nan!")
    
    def Play(self):
        nbOfPair = 4
        nbOfPairPlayerFound = 0

        self.lcd.Show("Demarrage...")
        time.sleep(3)

        isPlaying = True
        while isPlaying:
            
            uuidFirstCard = AskCard()
            
            time.sleep(1)
            
            uuidSecondCard = AskCard()
            
            time.sleep(1)

            CheckPair(uuidFirstCard, uuidSecondCard)
                    
            time.sleep(2)
            
            if(nbOfPair == nbOfPairPlayerFound):
                isPlaying = False
                
        self.lcd.Show("Victoire!")