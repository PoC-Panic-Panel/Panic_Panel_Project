import time
from dataclasses import dataclass, field
from enum import Enum, auto


import time
from dataclasses import dataclass, field
from enum import Enum, auto


class SessionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    WIN =auto()
    LOSE = auto()
    ABORTED = auto()


@dataclass
class GameSession:
    difficulty: str
    total_games: int
    time_limit: int
    start_time: float = field(default_factory=time.time)
    completed_games: int = 0
    failed_games: int = 0
    state: SessionState = SessionState.RUNNING
    
    def remaining_time(self) -> int:
        elapsed = time.time() - self.start_time
        remaining = self.time_limit - int(elapsed)
        return max(0, remaining)
    
    def is_finished(self) -> bool:
        if self.state in (SessionState.WIN, SessionState.LOSE, SessionState.ABORTED):
            return True
        
        if self.remaining_time() <= 0:
            self._compute_final_state()
            return True
            
        if self.completed_games + self.failed_games >= self.total_games:
            self._compute_final_state()
            return True
        
        return False
    
    def _compute_final_state(self):
        if self.completed_games == self.total_games and self.failed_games == 0:
            self.state = SessionState.WIN
        else:
            self.state = SessionState.LOSE
            
    def register_game_result(self, success: bool):
        if self.state != SessionState.RUNNING:
            return

        if success:
            self.completed_games += 1
        else:
            self.failed_games +=1
            
        if self.completed_games + self.failed_games >= self.total_games:
             self._compute_final_state()