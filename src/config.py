# PlayOK connection
DELAY = 5
WS_URL = "wss://x.playok.com:17003/ws/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
KEEP_ALIVE = {"i": []}
CREDENTIALS = {
    "i": [1710],
    "s": [
        "+639191544908807788",  # nnk6619g
        "en",
        "b",
        "",
        USER_AGENT,
    ]
}

# PlayOK socket opcodes
LOGIN_INFO = 18
USER_INFO = 61
ACTIVE_CHALLENGES = 70
JOIN_TABLE = 72
LEAVE_TABLE = 73
GAME_CHAT = 81
TAKE_SIDE = 83
LEAVE_SIDE = 84
START_GAME = 85
GAME_STATE = 90
LOAD_GAME = 91
LOAD_MOVE = 92
RESIGN_GAME = 93

# UCI chess engine
ENGINE_PATH = "../engine/abc.exe"
SEARCH_TIME = 3
WHITE = 1
BLACK = 0
NONE = -1