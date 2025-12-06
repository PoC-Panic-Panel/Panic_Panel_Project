from typing import Optional
import time
from RPLCD.i2c import CharLCD
from game_session import GameSession, SessionState


class DisplayManager:
    def __init__(self, i2c_address: int = 0x27):
        self._lcd: Optional[CharLCD] = CharLCD(
            i2c_expander='PCF8574',
            address=i2c_address,
            port=1,
            cols=16,
            rows=2
        )
        self.clear()
        self.show_message("Panic Panel","Serveur boot...")
        
    def clear(self):
        self._lcd.clear()
        
    def _write_lines(self, line1: str, line2: str =""):
        self._lcd.clear()
        self._lcd.write_string(line1[:16].ljust(16))
        self._lcd.crlf()
        self._lcd.write_string(line2[:16].ljust(16))
        
    def show_message(self, line1: str, line2: str =""):
        self._write_lines(line1, line2)
        
    def show_idle(self, difficulty: str):
        self._write_lines("Panic Panel", f"Diff: {difficulty}")
        
    def show_session(self, session: GameSession):
        remaining = session.remaining_time()
        line1 = f"T:{remaining:03d}s G:{session.completed_games}/{session.total_games}"
        line1 = line1[:16]
        
        if session.total_games > 0:
            ratio = session.completed_games / session.total_games
        else:
            ratio = 0.0
        bar_len = int(16*ratio)
        bar = "#" * bar_len + "-" * (16 - bar_len)
        
        self._write_lines(line1, bar)
    
    def show_result(self, session: GameSession):
        if session.state == SessionState.WIN:
            line1 = "VICTOIRE !"
        elif session.state == SessionState.LOSE:
            line1 = "ECHEC..."
        else:
            line1 = "TERMINE"
            
        line2 = f"{session.completed_games}/{session.total_games} reussis"
        self._write_lines(line1, line2)
        time.sleep(5)
                   
    def show_broker_status(self, connected: bool):
        if connected:
            self._write_lines("MQTT: CONNECTE", "Broker ok")
        else:
            self._write_lines("MQTT: OFF", "Check broker")
        time.sleep(1.5)