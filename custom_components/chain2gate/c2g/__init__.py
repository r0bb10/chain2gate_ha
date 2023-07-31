import websockets
import websocket
import json
import asyncio

import logging

LOG = logging.getLogger(__name__)

class Chain2Gate:
    """Chain2Gate class"""

    def __init__(self, hass, host: str) -> None:
        """Initialize."""
        self.hass = hass
        self.host = host
        self.ws_url = "ws://" + self.host + ":81"
        self._has_sensors = False
        self._running = True

    def check_connection(self) -> bool:
        """Check connection to WebSocket """
        # async with websockets.connect(...) as websocket:

        try:
            ws = websocket.WebSocket()
            ws.connect(self.ws_url)
            ws.send("!")
            msg = json.loads(ws.recv())
            self.id = msg["Chain2Info"]["Id"]
            self.ip = msg["Chain2Info"]["Ip"]
            self.prog_id = msg["Chain2Info"]["ProgId"]
            ws.close()
            LOG.info("Chain2Gate found: %s", self.id)
            return True
        except Exception:
            LOG.error("Chain2Gate not found: %s", self.host)
            return False
        
    async def connect(self) -> bool:
        """Connect to WebSocket and read info """
        self.check_connection()
        self.init_sensors()
        asyncio.create_task(self.connect_async())    
        LOG.info("Chain2Gate waiting for messages...")   
    
    async def connect_async(self):
        while self._running:
            async with websockets.connect(self.ws_url) as ws:
                self._ws = ws
                while self._running:
                    msg = await ws.recv()
                    await self.process_message(msg)        

    async def process_message(self, msg):
        msg = json.loads(msg)
        if "Chain2Data" in msg:
            print(msg)
            msg = msg["Chain2Data"]
            if msg["Type"] == "CF1": # trama quartoraria
                await self.sens_tariff_code.set_value(msg["Payload"]["TariffCode"])
                await self.sens_curr_quart_act_energy.set_value(msg["Payload"]["CurrQuartActEnergy"])
                await self.sens_instant_power.set_value(msg["Payload"]["InstantPower"])
                await self.sens_quart_average_power.set_value(msg["Payload"]["QuartAveragePower"])
                await self.sens_total_act_energy.set_value(msg["Payload"]["TotalActEnergy"])
            elif msg["Type"] == "CF21": # trama superamento 300 W
                await self.sens_instant_power.set_value(msg["Payload"]["InstantPower"])
        elif "Chain2Info" in msg:
            pass
        
    def init_sensors(self):
        if not self._has_sensors:
            self.sens_tariff_code = C2GSensor("Tariff Code")
            self.sens_curr_quart_act_energy = C2GSensor("Curr Quart Act Energy", "Wh", "energy")  
            self.sens_instant_power = C2GSensor("Instant Power", "W", "power")
            self.sens_quart_average_power = C2GSensor("Quart Average Power", "W", "power")
            self.sens_total_act_energy = C2GSensor("Total Act Energy", "Wh", "energy")
    
    def get_sensors(self):
        self.init_sensors()
        return [self.sens_tariff_code,
                self.sens_curr_quart_act_energy,
                self.sens_instant_power,
                self.sens_quart_average_power,
                self.sens_total_act_energy]
        
class C2GSensor:
    def __init__(self, name: str, unit: str = None, device_class: str = None):
        self.name = name
        self.value = None
        self.unit_of_measurement = unit
        self.device_class = device_class

    async def set_value(self, value):
        self.value = value
        print(self.name + ": " + str(self.value))
        if self._callback:
            print("callback")
            await self._callback()

    def set_callback(self, callback):
        self._callback = callback