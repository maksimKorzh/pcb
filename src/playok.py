# Packages
import json
import threading
import time
import websocket
from engine import ChessEngine
from config import *

'''

    For a joined table with self.active_table we need
    to answer the following questions:
    
    1. Is game active or not
    2. Who is in white/black slots?
    3. When start request is sent and timer is started
    4. When game starts
    5. When game ends

'''

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
        self.active_game = -1
        self.user_name = ""
        self.player_white = ""
        self.player_black = ""
        self.engine_side = -1
        
        # Chess engine
        self.engine = ChessEngine()

    # Reset PlayOK state
    def reset_state(self):
        self.active_table = 0
        self.active_game = -1
        self.player_white = ""
        self.player_black = ""
        self.engine_side = -1

    # Get user status
    def user_status(self):
        self.send_message({"i": [USER_INFO], "s": [self.user_name]})

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

    # Stay online
    def keep_alive(self):
        while self.running:
            time.sleep(5)
            if not self.running: break
            self.send_message(KEEP_ALIVE)

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
                #print(" ->:", end=" ")
                #print(message[:75] + "..." if len(message) > 75 else message)

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
                        first_table[-1] = "0"
                        first_table[-2] = "0"
                        first_table = int("".join(first_table))
                        last_table = first_table + 99
                        self.table_range = (first_table, last_table)
                        print(f"PLAYOK: Table range {self.table_range}")

                # User has been booted
                #if response["i"][0] == 25 and response["i"][1] == 0 and response["i"][2] == 0:
                    #print(f"LOBBY: {self.user_name} have been booted by the table operator")
                    #self.reset_state()
                
                if response["i"][0] == USER_INFO:
                    #print(f"INFO: {self.user_name} is at table {response["i"][2]}")
                    if response["i"][2] == 0: self.reset_state()
                
                #if self.user_name in message: print(message)

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
                            
                            # Table actions
                            elif table == self.active_table:
                                # Taking sits over the board
                                if response["i"][0] == ACTIVE_CHALLENGES:
                                    if response["i"][3] == 1: self.player_white = response["s"][1]
                                    if response["i"][4] == 1: self.player_black = response["s"][2]
                                    if response["i"][3] == 0: self.command("white", table)
                                    if response["i"][4] == 0: self.command("black", table)

                                # Tracking game status
                                elif response["i"][0] == GAME_STATE: self.active_game = response["i"][3]
                                
                                # Load ongoing game
                                elif response["i"][0] == LOAD_GAME:
                                    self.engine.new_game()
                                    try:
                                        moves = response["s"]
                                        for move in moves: self.engine.load_move(move)
                                        print(self.engine.board)
                                        print(f"SYSTEM: Loaded game at table #{self.active_table}")
                                    except: pass
                                
                                # Load last move
                                elif response["i"][0] == LOAD_MOVE and response["i"][1] == self.active_table:
                                    try:
                                        #print("move", response)
                                        side = 1 if self.engine.board.turn else 0
                                        move = response["s"][0]
                                        self.engine.load_move(move)
                                        print("\n", self.engine.board, sep="")
                                        print("Side to move:", "white" if self.engine.board.turn else "black")
                                        if side == self.engine_side ^ 1: self.send_move()
                                    except: pass

                                # User has been displaced
                                if response["i"][0] == GAME_CHAT:
                                    if response["s"][0] == "+ you have been displaced by the table operator":
                                        print(f"TABLE #{table}: {self.user_name} has been displaced by the table operator")
                                        self.command("leave", table)
                                        continue

                                

                                # Init game status
                                status = "idling" if self.active_game == -1 else "playing"
                                
                                # Request to start the game
                                if status == "idling":
                                    if self.engine_side == 0 and self.player_white == self.user_name and self.player_black:
                                        print(f"TABLE #{table}: {self.user_name} requests start as white")
                                    if self.engine_side == 1 and self.player_black == self.user_name and self.player_white:
                                        print(f"TABLE #{table}: {self.user_name} requests start as black")

                                # Check user status
                                self.user_status()

                                # Print table status
                                print(f"TABLE #{table}: ({self.player_white}) vs ({self.player_black}) {status}")

                    except Exception as e: pass#print(e)

            except Exception as e:
                print("SYSTEM:", e)
                self.running = False
                break

    def send_move(self):
        move = self.engine.search()
        self.send_message({"i": [LOAD_MOVE, self.active_table, 1, move, 1]})

    def accept_challenge(self, color, table):
        self.command("join", table)
        #self.command(color, table)
        #print(f"TABLE #{table}")
        
        
        
        #self.command('start', table)

    def command(self, action, table):
        request = {"i": [], "s": []}
        if action == "join":
            request["i"] = [JOIN_TABLE, table]
            self.active_table = table
            self.engine_side = -1
            print(f"TABLE #{table}: Joined table")
        elif action == "leave":
            print(f"TABLE #{table}: Left table")
            request["i"] = [LEAVE_TABLE, table]
            self.active_table = 0
            self.active_game = -1
            self.player_white = ""
            self.player_black = ""
            self.engine_side = -1
        elif action == "white":
            request["i"] = [TAKE_SIDE, table, 0]
            self.engine_side = 1
        elif action == "black":
            request["i"] = [TAKE_SIDE, table, 1]
            self.engine_side = 0
        elif action == "start":
            request["i"] = [START_GAME, table]
        #    print(f"PLAYOK: Attempting to start a game at table #{table}")
        #    self.send_message(request)
        elif action == "resign":
          request["i"] = [RESIGN_GAME, table, 4, 0]
        
        # Send user action to PlayOK
        #if action != "start": self.send_message(request)
        self.send_message(request)
        
        # Clear if anything goes wrong
        self.user_status()
        