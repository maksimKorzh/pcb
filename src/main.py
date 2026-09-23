from playok import PlayOK
import json

if __name__ == "__main__":
    #websocket.enableTrace(True)
    socket = PlayOK()

    socket.connect()

    while socket.running:
        message = input()

        if message.lower() == "quit":
            socket.close()
            continue
        
        elif "join" in message:
            socket.send_command('join', int(message.split()[-1]))
            continue
        
        #elif message == "white" or message == "black" or message == "start" or message == "resign":
        elif message in [
            "white_on", "white_off",
            "black_on", "black_off",
            "start", "resign"
        ]:
            socket.send_command(message, socket.active_table)
            continue
        
        elif "leave" in message:
            socket.send_command('leave', socket.active_table)
            continue
        
        elif message == "info":
            print("running:", socket.running)
            print("active table:", socket.active_table)
            print("player white:", socket.player_white)
            print("player black:", socket.player_black)
            print("active game:", socket.active_game)
            print("engine side:", socket.engine_side)
            print("first move:", socket.first_move)
            continue
        
        elif message == "user":
            socket.user_status()
            continue

        elif message == "move":
            socket.send_move()
            continue
        
        elif message == "board":
            print(socket.engine.board)
            continue

        try: socket.send_message(json.loads(message))
        except: print("Bad JSON")