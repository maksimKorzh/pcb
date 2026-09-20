# Packages
import json
import threading
import time
import websocket
from config import *

# PlayOK WebSocket connection
class PlayOK:
    # Init runtime
    def __init__(self):
        # WebSocket connection
        self.ws = None
        self.keep_alive_thread = None
        self.receive_thread = None
        self.running = False
        
        # PlayOK state
        self.active_game = 0
        self.joined_table = 0
        self.active_table = 0
        self.side_to_move = 0
        self.engine_side = -1

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
                print("SYSTEM: WebSocket connection closed")
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
                if DEBUG:
                    print("SOCKET <-:", end=" ")
                    print(message[:75] + "..." if len(message) > 75 else message)
            except Exception as e:
                print("SYSTEM:", e)
                self.running = False

    # Receive message from PlayOK WebSocket
    def receive_messages(self):
        while self.running:
            try:
                message = self.ws.recv()
                if not message: continue
                try:
                    #if DEBUG:
                    #    print("SOCKET ->:", end=" ")
                    #    print(message[:75] + "..." if len(message) > 75 else message)

                    response = json.loads(message)
                    
                    # TODO:
                    # 1. Change user to guest
                    # 2. Maybe store time control
                    
                    # Challenges & ongoing games
                    if response["i"][0] == 70:
                        print(message)
                        table = response["i"][1]
                        player1 = response["i"][1]
                        player2 = response["i"][2]
                        if self.joined_table == 1: return
                        if response["i"][3] == 1 and response["i"][4] == 0: self.accept_challenge('white', table)
                        if response["i"][3] == 0 and response["i"][4] == 1: self.accept_challenge('black', table)
                        

                    
                    
                    
                except json.JSONDecodeError: pass
            except Exception as e:
                print("SYSTEM:", e)
                self.running = False
                break

    def accept_challenge(self, color, table):
        self.message('join', table)
        self.message(color, table)
        self.message('start', table)

    def message(self, action, table):
        request = {"i": [], "s": []}
        if action == "join":
            request["i"] = [72, table]
            self.joined_table = 1
            self.active_table = table
            self.engine_side = -1
            print(f"PLAYOK: Joined table #{table}")
        elif action == "leave":
            print(f"PLAYOK: Leaving table #{table}")
            # send "ucinewgame" to engine
            request["i"] = [73, table]
            self.active_game = 0
            self.joined_table = 0
            self.active_table = 0
            self.side_to_move = 0
            self.engine_side = -1
        elif action == "white":
            request["i"] = [83, table, 1]
            self.engine_side = 1
            print(f"PLAYOK: Took white pieces at table #{table}")
        elif action == "black":
            request["i"] = [83, table, 0]
            self.engine_side = 0
            print(f"PLAYOK: Took black pieces at table #{table}")
        elif action == "start":
            self.active_game = 0
            #request["i"] = [85, table]
            print(f"PLAYOK: Attempting to start a game at table #{table}")
            '''
              setTimeout(function() {
                if (!activeGame) {
                  console.log('playok: opponent refused to start game at table #' + table);
                  message(socket, 'leave', table);
                } else if (activeGame) {
                  if (katagoSide == 0) {
                    katago.stdin.write('clear_board\n');
                    katago.stdin.write('genmove B\n');
                    katago.stdin.write('showboard\n');
                  }
                }
              }, 5000);
            '''
        elif action == "resign":
          request["i"] = [93, table, 4, 0]
        
        # Send user action to PlayOK
        self.send_message(request)