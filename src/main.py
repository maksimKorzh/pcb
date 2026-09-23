from playok import PlayOK
import json
from config import *

if __name__ == "__main__":
    socket = PlayOK()
    socket.connect()

    while socket.running:
        message = input()

        if message.lower() == "quit":
            socket.close()
            continue

        elif message in ["resign", "leave"]:
            socket.send_command(message, socket.active_table)
            continue

        elif message == "info":
            print("running:", socket.running)
            print("active table:", socket.active_table)
            print("player white:", socket.player_white)
            print("player black:", socket.player_black)
            print("active game:", "Idle" if socket.active_game == NONE else "Play")
            print("engine side:", "None" if socket.engine_side == NONE else "White" if socket.engine_side == WHITE else "Black")
            print("first move:", "No" if socket.first_move == NONE else "Played")
            continue
        
        elif message == "board":
            print(socket.engine.board)
            continue

        try: socket.send_message(json.loads(message))
        except: print("Bad JSON")