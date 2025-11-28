import random

class CardVerifier:
    def __init__(self):
        self.cardsNotFound = self.__AssignColorsShuffled()
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
    
    def __AssignColorsShuffled(self):
        uuids = ["202186105173",
                 "42766173", 
                 "17037184174",
                 "5810543166", 
                 "104621165",
                 "10624095174",
                 "122152174",
                 "23480172174"
                ]
        colors = ["jaune", "rouge", "bleu", "vert"]

        n = len(uuids)
        k = len(colors)

        color_pool = []
        for i in range(n):
            color_pool.append(colors[i % k])

        random.shuffle(color_pool)

        return {uid: color_pool[i] for i, uid in enumerate(uuids)}