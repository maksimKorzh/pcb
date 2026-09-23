# Packages
from playok import PlayOK
import json
from config import *

# Connect to PlayOK
playok = PlayOK()
playok.connect()

# PlayOK session is active
while playok.running:
    # Read user input
    message = input()

    # Quit PlayOK session
    if message.lower() == "quit":
        playok.close()
        continue

    # Resign the game
    elif message == "resign":
        playok.send_command(message, playok.active_table)
        continue

    # Inspect PlayOK session
    elif message == "info":
        print("running:", playok.running)
        print("active table:", playok.active_table)
        print("player white:", playok.player_white)
        print("player black:", playok.player_black)
        print("active game:", "Idle" if playok.active_game == NONE else "Play")
        print("engine side:", "None" if playok.engine_side == NONE else "White" if playok.engine_side == WHITE else "Black")
        print("first move:", "No" if playok.first_move == NONE else "Played")
        continue

    # Print engine board to console
    elif message == "board":
        print(playok.engine.board)
        continue