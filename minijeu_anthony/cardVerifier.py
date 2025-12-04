import random

class CardVerifier:
    def __init__(self):
        self.cards_not_found = self.__assign_colors_shuffled()
        self.cards_found = []
    
    def is_same_card(self, uuid_first_card, uuid_second_card):
        if(uuid_first_card == uuid_second_card):
            return True
        return False
    
    def is_a_pair(self, uuid_first_card, uuid_second_card):        
        if(self.cards_not_found[uuid_first_card] == self.cards_not_found[uuid_second_card]):
            self.cards_found.append(uuid_first_card)
            self.cards_found.append(uuid_second_card)
            return True
        return False
        
    def is_a_card_in_the_game(self, noCard):
        if(noCard in self.cards_not_found):
            return True
        return False
    
    def is_a_pair_found(self, uuid_first_card, uuid_second_card):
        if(uuid_first_card in self.cards_found and uuid_second_card in self.cards_found):
            return True
        return False
    
    def get_value(self, uuid):
        return self.cards_not_found[uuid]
    
    def __assign_colors_shuffled(self):
        uuids = ["202186105173",
                 "42766173", 
                 "17037184174",
                 "5810543166", 
                 "104621165",
                 "10624095174",
                 "122152174",
                 "23480172174"
                ]
        colors = ["Jaune", "Rouge", "Bleu", "Vert"]

        n = len(uuids)
        k = len(colors)

        color_pool = []
        for i in range(n):
            color_pool.append(colors[i % k])

        random.shuffle(color_pool)

        return {uid: color_pool[i] for i, uid in enumerate(uuids)}