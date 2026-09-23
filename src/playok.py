# Packages
import json
import time
import random
import threading
import websocket
from engine import ChessEngine
from config import *

# PlayOK WebSocket connection
class PlayOK:
    # Init runtime
    def __init__(self):
        # WebSocket state
        self.ws = None
        self.keep_alive_thread = None
        self.receive_thread = None
        self.running = False
        
        # PlayOK state
        self.table_range = (0, 0)
        self.active_table = 0
        self.active_game = NONE
        self.user_name = ""
        self.player_white = ""
        self.player_black = ""
        self.engine_side = NONE
        self.first_move = NONE
        
        # Chess engine
        self.engine = ChessEngine()

    # Reset PlayOK state
    def reset_state(self):
        self.active_table = 0
        self.active_game = NONE
        self.player_white = ""
        self.player_black = ""
        self.engine_side = NONE
        self.first_move = NONE

    # Connect to PlayOK WebSocket
    def connect(self):
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(WS_URL, origin="null", header=["User-Agent: " + USER_AGENT])
            self.running = True
            self.send_message(CREDENTIALS)
            self.keep_alive_thread = threading.Thread(target=self.keep_alive, daemon=True)
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.keep_alive_thread.start()
            self.receive_thread.start()
        except Exception as e:
            print("SYSTEM: WebSocket connection error:", e)
            self.running = False

    # Disconnect from PlayOK Websocket
    def close(self):
        self.running = False
        if self.ws:
            try:
                self.ws.close()
                self.engine.close()
                print("SYSTEM: WebSocket connection closed")
                print("SYSTEM: Chess engine closed")
            except Exception: pass

    # Get user status
    def user_status(self):
        self.send_message({"i": [USER_INFO], "s": [self.user_name]})

    # Stay online
    def keep_alive(self):
        while self.running:
            time.sleep(DELAY)
            if not self.running: break
            self.send_message(KEEP_ALIVE)
            
            # Check user status
            self.user_status()
            

    # Send message to PlayOK WebSocket
    def send_message(self, message):
        if not self.ws or not self.running:
            print("SYSTEM: WebSocket is not connected")
            return
        if isinstance(message, dict):
            message = json.dumps(message, separators=(",", ":"))
            try:
                self.ws.send(message)
                #print(" <-:", end=" ")
                #print(message[:75] + "..." if len(message) > 75 else message)
            except Exception as e:
                print("SYSTEM:", e)
                self.running = False

    # Receive message from PlayOK WebSocket
    def receive_messages(self):
        while self.running:
            try:
                
                
                message = self.ws.recv()
                if not message: continue
                response = json.loads(message)
                
                # Player user name
                if response["i"][0] == LOGIN_INFO:
                    if self.user_name == "":
                        self.user_name = response["s"][0]
                        print(f"PLAYOK: Logged in as \"{self.user_name}\"")
                
                # Init table range
                if response["i"][0] == ACTIVE_CHALLENGES:
                    table = response["i"][1]
                    if self.table_range == (0, 0):
                        first_table = [c for c in str(table)]
                        first_table[NONE] = "0"
                        first_table[-2] = "0"
                        first_table = int("".join(first_table))
                        last_table = first_table + 99
                        self.table_range = (first_table, last_table)
                        print(f"PLAYOK: Table range {self.table_range}")

                if response["i"][0] == USER_INFO:
                    #print(f"INFO: {self.user_name} is at table {response["i"][2]}")
                    if response["i"][2] == 0: self.reset_state()
                    else: self.active_table = response["i"][2]

                # Entered the room
                if self.table_range[0]:
                    try:
                        # Table action in player room
                        if response["i"][1] in range(self.table_range[0], self.table_range[1]):
                            # Init table
                            table = response["i"][1]

                            # Lobby actions
                            if not self.active_table:
                                if response["i"][0] == ACTIVE_CHALLENGES:
                                    print(f"LOBBY: Game ({response["s"][1]}) vs ({response["s"][2]}) at #{table}")
                                    
                                    # Join empty table
                                    if response["i"][3] == 0 and response["i"][4] == 0:
                                        self.send_command("join", table)
                                        if random.choice([WHITE, BLACK]) == WHITE: self.send_command("white_on", table)
                                        else: self.send_command("black_on", table)
                                        continue
                            
                            # Table actions
                            elif table == self.active_table:
                                # Taking sits over the board
                                if response["i"][0] == ACTIVE_CHALLENGES:
                                    
                                    # Init players
                                    self.player_white = response["s"][1]
                                    self.player_black = response["s"][2]
                                    
                                    # Init engine side
                                    if self.player_white == self.user_name: self.engine_side = WHITE
                                    elif self.player_black == self.user_name: self.engine_side = BLACK

                                # Tracking game status
                                elif response["i"][0] == GAME_STATE: self.active_game = response["i"][3]
                                
                                # Load ongoing game
                                elif response["i"][0] == LOAD_GAME:
                                    self.engine.new_game()
                                    try:
                                        moves = response["s"]
                                        for move in moves: self.engine.load_move(move)
                                        #print(self.engine.board)
                                        print(f"TABLE #{table}: Loaded game")
                                    except: pass
                                
                                # Load last move
                                elif response["i"][0] == LOAD_MOVE:
                                    try:
                                        side = 1 if self.engine.board.turn else 0
                                        move = response["s"][0]
                                        print(f"TABLE #{table}: {("white" if side else "black")} played {move}")
                                        self.engine.load_move(move)
                                        if side == self.engine_side ^ 1: self.send_move()
                                    except: pass

                                # User has been displaced
                                if response["i"][0] == GAME_CHAT:
                                    if response["s"][0] == "+ you have been displaced by the table operator":
                                        self.send_command("leave", table)
                                        continue

                                # Init game status
                                status = "idle" if self.active_game == NONE else "play"

                                # Print table status
                                if self.first_move == NONE:
                                    print(f"TABLE #{table}: ({self.player_white}) vs ({self.player_black}) {status}")
                                
                                # Request to start the game
                                if status == "idle":
                                    if self.first_move != NONE:
                                        self.send_command("leave", table)
                                        time.sleep(DELAY)
                                    if self.engine_side != NONE:
                                        if self.player_white != "" and self.player_black != "":
                                            self.send_command("start", table)
                                            time.sleep(DELAY)
                                        elif self.player_white == "" and self.player_black == "":
                                            self.send_command("leave", table)

                                elif status == "play" and self.player_white != self.user_name and self.player_black != self.user_name:
                                    self.send_command("leave", table)
                                    time.sleep(DELAY)
                                
                                elif status == "play" and self.engine_side == WHITE and self.first_move == NONE:
                                    self.send_move();
                                    self.first_move = WHITE
                                
                                elif status == "play" and self.engine_side == BLACK and self.first_move == NONE:
                                    self.first_move = WHITE

                    except Exception as e: pass#print(e)

            except Exception as e:
                print("SYSTEM:", e)
                self.running = False
                break

    def send_move(self):
        move = self.engine.search()
        self.send_message({"i": [LOAD_MOVE, self.active_table, 1, move, 1]})

    def send_command(self, action, table):
        # Command template
        request = {"i": [], "s": []}
        
        # Pick user command
        if action == "join": request["i"] = [JOIN_TABLE, table]
        elif action == "leave": request["i"] = [LEAVE_TABLE, table]
        elif action == "white_on": request["i"] = [TAKE_SIDE, table, 0]
        elif action == "white_off": request["i"] = [LEAVE_SIDE, table, 0]
        elif action == "black_on": request["i"] = [TAKE_SIDE, table, 1]
        elif action == "black_off": request["i"] = [LEAVE_SIDE, table, 1]
        elif action == "start": request["i"] = [START_GAME, table]
        elif action == "resign": request["i"] = [RESIGN_GAME, table, 4, 0]
        
        # Send user command to PlayOK
        self.send_message(request)
        
        self.user_status()
        
