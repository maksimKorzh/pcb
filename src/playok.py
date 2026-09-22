# Packages
import json
import threading
import time
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
        self.table_range = 0
        self.active_game = 0
        self.joined_table = 0
        self.active_table = 0
        #self.side_to_move = 0
        self.engine_side = -1
        
        # Chess engine
        self.engine = ChessEngine()

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
                #print(message)
                #print(message[:75] + "..." if len(message) > 75 else message, self.joined_table, self.active_table)
                
                #print(self.joined_table, self.active_table, self.engine_side)

                response = json.loads(message)
                
                # Player nickname
                if response["i"][0] == LOGIN_INFO: print(f"PLAYOK: Logged in as \"{response["s"][0]}\"")
                
                # Challenges & ongoing games
                elif response["i"][0] == ACTIVE_CHALLENGES:
                    table = response["i"][1]
                    if not self.table_range:
                        first_table = [c for c in str(table)]
                        first_table[-1] = "0"
                        first_table[-2] = "0"
                        first_table = "".join(first_table)
                        last_table = str(int(first_table) + 99)
                        self.table_range = "#" + first_table + " - " + "#" + last_table
                        print(f"PLAYOK: Table range {self.table_range}")
                    if self.joined_table == 1: continue
                    #if response["i"][3] == 1 and response["i"][4] == 0: self.accept_challenge('white', table)
                    #if response["i"][3] == 0 and response["i"][4] == 1: self.accept_challenge('black', table)
                    
                    #if response["i"][3] == 1 and response["i"][4] == 1: self.accept_challenge('black', table)
                    
                    # {"i": [72, 152], "s": []}
                    
                    
                # Load ongoing game
                elif response["i"][0] == LOAD_GAME and response["i"][1] == self.active_table and self.joined_table:
                    self.engine.new_game()
                    try:
                        moves = response["s"]
                        for move in moves: self.engine.load_move(move)
                        print(self.engine.board)
                        print(f"SYSTEM: Loaded game at table #{self.active_table}")
                    except: pass

                # Load last move
                elif response["i"][0] == LOAD_MOVE and response["i"][1] == self.active_table and self.joined_table:
                    try:
                        print("move", response)
                        side = 1 if self.engine.board.turn else 0
                        move = response["s"][0]
                        self.engine.load_move(move)
                        print(self.engine.board)
                        if side == self.engine_side ^ 1: self.send_move()
                    except: pass

                # Leave when game is not available
                if response["i"][0] == GAME_CHAT and response["i"][1] == self.active_table:
                      print('PLAYOK:', response["s"][0])
                      if "resigns" in response["s"][0] or  \
                         "exceeded" in response["s"][0] or \
                         "booted" in response["s"][0] or   \
                         "offline" in response["s"][0] or  \
                         "displaced" in response["s"][0]:
                          self.message('leave', response["i"][1])

                # Check if the game is still played
                if response["i"][0] == GAME_STATE:
                    if response["i"][3] == -1: self.active_game = 0
                    else: self.active_game = 1
                    
            except Exception as e:
                print("SYSTEM:", e)
                self.running = False
                break

    def send_move(self):
        move = self.engine.search()
        self.send_message({"i": [LOAD_MOVE, self.active_table, 1, move, 1]})
        print("best move", {"i": [LOAD_MOVE, self.active_table, 1, move, 1]})

    def accept_challenge(self, color, table):
        self.message('join', table)
        self.message(color, table)
        self.message('start', table)

    def message(self, action, table):
        request = {"i": [], "s": []}
        if action == "join":
            request["i"] = [JOIN_TABLE, table]
            self.joined_table = 1
            self.active_table = table
            self.engine_side = -1
            print(f"PLAYOK: Joined table #{table}")
        elif action == "leave":
            print(f"PLAYOK: Leaving table #{table}")
            request["i"] = [LEAVE_TABLE, table]
            self.active_game = 0
            self.joined_table = 0
            self.active_table = 0
            self.engine_side = -1
        elif action == "white":
            request["i"] = [TAKE_SIDE, table, 0]
            self.engine_side = 1
            print(f"PLAYOK: Took white pieces at table #{table}")
        elif action == "black":
            request["i"] = [TAKE_SIDE, table, 1]
            self.engine_side = 0
            print(f"PLAYOK: Took black pieces at table #{table}")
        elif action == "start":
            self.active_game = 0
            request["i"] = [START_GAME, table]
            print(f"PLAYOK: Attempting to start a game at table #{table}")
            self.send_message(request)
            time.sleep(5)
            if not self.active_game:
                print(f"PLAYOK: Opponent refused to start game at table #{table}")
                self.message('leave', table)
            elif self.active_game:
                if self.engine_side == 1: self.send_move()
        elif action == "resign":
          request["i"] = [RESIGN_GAME, table, 4, 0]
        
        # Send user action to PlayOK
        if action != "start": self.send_message(request)