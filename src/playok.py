import json
import threading
import time
import websocket
from config import *

class PlayOK:
    def __init__(self):
        self.ws = None
        self.keep_alive_thread = None
        self.receive_thread = None
        self.running = False

    def connect(self):
        try:
            self.ws = websocket.WebSocket()

            self.ws.connect(
                WS_URL,
                origin="null",
                header=[ "User-Agent: " + USER_AGENT ]
            )

            print("PLAYOK: Connected to WebSocket")

            self.running = True
            self.send_message(CREDENTIALS);

            self.keep_alive_thread = threading.Thread(
                target=self._keep_alive,
                daemon=True
            )
            
            self.receive_thread = threading.Thread(
                target=self._receive_messages,
                daemon=True
            )
            
            self.keep_alive_thread.start()
            self.receive_thread.start()

        except Exception as e:
            print("PLAYOK: WebSocket connection error:", e)
            self.running = False

    def _receive_messages(self):
        while self.running:
            try:
                message = self.ws.recv()
                if not message: continue
                
                try:
                    response = json.loads(message)
                    print("PLAYOK ->:", end=" ")
                    print(response)
                except json.JSONDecodeError:
                    print("PLAYOK: Not JSON")

            except websocket.WebSocketConnectionClosedException:
                print("PLAYOK: WebSocket connection closed")
                self.running = False
                break

            except Exception as e:
                print("PLAYOK: Receive error:", e)
                self.running = False
                break

    def _keep_alive(self):
        while self.running:
            time.sleep(5)
            if not self.running: break
            self.send_message(KEEP_ALIVE)
            
    def send_message(self, message):
        if not self.ws or not self.running:
            print("PLAYOK: WebSocket is not connected")
            return

        if isinstance(message, dict):
            message = json.dumps(message, separators=(",", ":"))
            try:
                self.ws.send(message)
                if DEBUG:
                    print("PLAYOK <-:", end=" ")
                    print(message)
            except Exception as e:
                print("PLAYOK: Send error:", e)
                self.running = False

    def close(self):
        self.running = False
        if self.ws:
            try:
                self.ws.close()
                print("PLAYOK: WebSocket connection closed")
            except Exception: pass