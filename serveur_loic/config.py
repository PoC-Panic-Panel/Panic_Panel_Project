MQTT_HOST = "10.4.1.47"
MQTT_PORT = 1883

TOPIC_GAME_STATUS = "panic/game/+/status"

TOPIC_SESSION_NEW = "panic/server/session"

ALL_GAMES = [
    "rfid-memory",
    "panic-sound",
    "chifoumi",
    # "cadenas",
    # "speed-simons",
]

DIFFICULTY_SETTINGS = {
    "EASY": {"time_limit": 120, "games_count": 2},
    "MEDIUM": {"time_limit": 90, "games_count": 3},
    "HARD": {"time_limit": 60, "games_count": 4},
}

# DIFFICULTY_GAMES = {
#     "EASY": ["rfid_memory"],
#     "MEDIUM": ["rfid_memory"],
#     "HARD": ["rfid_memory"],
# }

PIN_LED_BROKER = 17
PIN_LED_SERVICE = 27

PIN_LED_EASY = 22
PIN_LED_MEDIUM = 10
PIN_LED_HARD = 9

PIN_LED_START = 11

PIN_BTN_EASY = 5
PIN_BTN_MEDIUM = 6
PIN_BTN_HARD = 13
PIN_BTN_START = 19