# Panic Panel – Serveur (Pi maître)

Serveur Python qui orchestre la partie, affiche un timer (simulation), pilote les mini‑jeux via MQTT et calcule WIN/LOSE.

## ⚙️ Prérequis
- Python 3.10+
- Broker MQTT (VM Mosquitto, port 1883)

## 🚀 Simulation (sans GPIO)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export MQTT_HOST=192.168.10.20
export MQTT_PORT=1883
export MQTT_USER=panicuser
export MQTT_PASS='Pan1c!2025'
export SIMULATE=1

python master_server.py
```

## 🧪 Test rapide
```bash
mosquitto_sub -h $MQTT_HOST -p $MQTT_PORT -u $MQTT_USER -P "$MQTT_PASS" -t 'panic/#' -v
# Dans le serveur: start easy
# Remplace SESSION_ID par celui annoncé
mosquitto_pub -h $MQTT_HOST -p $MQTT_PORT -u $MQTT_USER -P "$MQTT_PASS"   -t 'panic/game/rfid-memory/status' -m '{"sessionId":"SESSION_ID","state":"SUCCESS"}'
```

## Topics
- panic/session/announce | tick | end
- panic/game/<id>/cmd | status
- (opt) panic/control/start
