class CardVerifier:
    def __init__(self):
        self.cardsNotFound = {
            "202186105173" : "jaune",
            "42766173" : "rouge",
            "17037184174" : "bleu",
            "5810543166" : "vert",
            "104621165" : "jaune",
            "10624095174" : "rouge",
            "122152174" : "bleu",
            "23480172174" : "vert",
        }
        self.cardsFound = []
    
    def IsSameCard(self, uuidFirstCard, uuidSecondCard):
        if(uuidFirstCard == uuidSecondCard):
            return True
        return False
    
    def IsAPair(self, uuidFirstCard, uuidSecondCard):        
        if(self.cardsNotFound[uuidFirstCard] == self.cardsNotFound[uuidSecondCard]):
            self.cardsFound.append(uuidFirstCard)
            self.cardsFound.append(uuidSecondCard)
            return True
        return False
        
    def IsACardInTheGame(self, noCard):
        if(noCard in self.cardsNotFound):
            return True
        return False
    
    def IsAPairFound(self, uuidFirstCard, uuidSecondCard):
        if(uuidFirstCard in self.cardsFound and uuidSecondCard in self.cardsFound):
            return True
        return False
    
    def GetValue(self, uuid):
        return self.cardsNotFound[uuid]