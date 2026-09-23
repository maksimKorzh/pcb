# Packages
import chess
import chess.engine
from config import *

'''

       a  b  c  d  e  f  g  h
8      0  1  2  3  4  5  6  7
7      8  9 10 11 12 13 14 15
6     16 17 18 19 20 21 22 23
5     24 25 26 27 28 29 30 31
4     32 33 34 35 36 37 38 39
3     40 41 42 43 44 45 46 47
2     48 49 50 51 52 53 54 55
1     56 57 58 59 60 61 62 63

'''
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
        move = source | (target << 6)
        if result.move.promotion: move |= (1 << 12)
        return move

    # Terminate engine
    def close(self):
        if self.engine is not None:
            self.engine.quit()
            self.engine = None

#engine = ChessEngine()
#engine.load_move("e4")
#engine.search()
#engine.close()