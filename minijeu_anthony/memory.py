from cardVerifier import CardVerifier
import time
import threading

class Memory:
    def __init__(self, reader, lcd, led_controller, mqtt):
        self.reader = reader
        self.verifier = CardVerifier()
        self.lcd = lcd
        self.led_controller = led_controller
        self.mqtt = mqtt
        self.nb_of_pair_player_found = 0
        self.nb_of_pair = 4
        self.on_card_received = threading.Event() 
        
    def __ask_card(self):
        card_is_good = False
        while card_is_good != True:
            self.lcd.show("Faite passer une carte")
            uuid_card = self.reader.read()
            if(self.verifier.is_a_card_in_the_game(uuid_card)):
                value = self.verifier.get_value(uuid_card)
                self.lcd.show(value)
                card_is_good = True
            else:
                self.lcd.show("Erreur de lecture")
                time.sleep(1)
                
        return uuid_card      

    def __check_pair(self, uuid_first_card, uuid_second_card):
        if(self.verifier.is_same_card(uuid_first_card, uuid_second_card)):
            self.lcd.show("Meme carte")
        elif(self.verifier.is_a_pair_found(uuid_first_card, uuid_second_card)):
            self.lcd.show("Paire deja trouvee")
        else:
            if(self.verifier.is_a_pair(uuid_first_card, uuid_second_card)):
                self.lcd.show("C'est une paire!")
                self.nb_of_pair_player_found = self.nb_of_pair_player_found + 1
            else:
                self.lcd.show("Nan nan nan!")
                
    def is_finised(self):
        if self.mqtt.stop_event.is_set():
            self.lcd.show("Partie stoppée")
            return True
        return False
    
    def play(self):        
        self.led_controller.light_red_on()
        self.mqtt.wait_for_start()
        self.led_controller.light_green_on()

        is_playing = True
        while is_playing:
            
            if(self.is_finised()):
                return
            
            uuid_first_card = self.__ask_card()
            
            if(self.is_finised()):
                return
            
            time.sleep(1)
            
            uuid_second_card = self.__ask_card()
                       
            if(self.is_finised()):
                return
            
            time.sleep(1)

            self.__check_pair(uuid_first_card, uuid_second_card)
                    
            time.sleep(1)
            
            if(self.nb_of_pair == self.nb_of_pair_player_found):
                is_playing = False
                
        self.lcd.show("Victoire!")
        self.mqtt.publish_state()