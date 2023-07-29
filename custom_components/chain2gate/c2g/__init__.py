from websockets.sync.client import connect
import json

class Chain2Gate:
    """Chain2Gate class"""

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    def connect(self) -> bool:
        """Connect to WebSocket and read info"""
        try:
            ws = connect("ws://" + self.host + ":81")
            ws.send("!")
            msg = json.loads(ws.recv())
            
            self.id = msg["Chain2Info"]["Id"]
            # self.ssid = msg["Chain2Info"]["Ssid"]
            self.ip = msg["Chain2Info"]["Ip"]
            # self.prog_id = msg["Chain2Info"]["ProgId"]
            # self.du = msg["Chain2Info"]["DU"]

            self.ws = ws
            return True
        except Exception:
            return False
        
class C2GSensor:
    def __init__(self, name: str):
        self.name = name