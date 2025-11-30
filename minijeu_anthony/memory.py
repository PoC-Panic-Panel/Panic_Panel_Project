from cardVerifier import CardVerifier
import time

class Memory:
    def __init__(self, reader, lcd, ledController):
        self.reader = reader
        self.verifier = CardVerifier()
        self.lcd = lcd
        self.ledController = ledController
        self.nbOfPairPlayerFound = 0
        self.nbOfPair = 4
        
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
                self.nbOfPairPlayerFound = self.nbOfPairPlayerFound + 1
            else:
                self.lcd.Show("Nan nan nan!")
    
    def Play(self):
        self.lcd.Show("Demarrage...")
        time.sleep(3)
        self.ledController.OnLightGreen()

        isPlaying = True
        while isPlaying:
            
            uuidFirstCard = self.__AskCard()
            
            time.sleep(1)
            
            uuidSecondCard = self.__AskCard()
            
            time.sleep(1)

            self.__CheckPair(uuidFirstCard, uuidSecondCard)
                    
            time.sleep(2)
            
            if(self.nbOfPair == self.nbOfPairPlayerFound):
                isPlaying = False
                
        self.lcd.Show("Victoire!")
        time.sleep(3)