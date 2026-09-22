# Packages
import chess
import chess.engine
from config import *

# Chess engine class
class ChessEngine:
    # Create chess board
    def __init__(self):
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    # Start a new game
    def new_game(self):
        self.board.reset()

    # Play move on engine board
    def load_move(self, move):
        try: self.board.push_san(move)
        except ValueError as e:
            raise ValueError(
                f"Invalid move '{move}' at position {self.board.fullmove_number}: {e}"
            )

    # Make engine move
    def search(self):
        result = self.engine.play(self.board.copy(), chess.engine.Limit(time=SEARCH_TIME))
        source = result.move.from_square ^ 56
        target = result.move.to_square ^ 56
        return source | (target << 6)

    # Terminate engine
    def close(self):
        if self.engine is not None:
            self.engine.quit()
            self.engine = None

#engine = ChessEngine()
#engine.load_move("e4")
#engine.search()
#engine.close()