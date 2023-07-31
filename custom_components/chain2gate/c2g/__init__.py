import websockets
import json
import asyncio

import logging

from homeassistant.const import UnitOfPower, UnitOfEnergy
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)

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

    async def check_connection(self, log_success: bool = True) -> bool:
        """Check connection to WebSocket """
        try:
            async with websockets.connect(self.ws_url) as ws:
                await ws.send("!")
                msg = await ws.recv()
                data = json.loads(msg)
                self.id = data["Chain2Info"]["Id"]
                self.ip = data["Chain2Info"]["Ip"]
                self.prog_id = data["Chain2Info"]["ProgId"]
                if log_success:
                    LOG.info("Chain2Gate found: %s", self.id)
                return True
        except Exception:
            LOG.error("Chain2Gate not found: %s", self.host)
            return False
        
    async def connect(self) -> bool:
        """Connect to WebSocket and read info """
        while not await self.check_connection():
            LOG.warning("Chain2Gate not found: %s", self.host)
            LOG.warning("Retrying in 10 seconds...")
            await asyncio.sleep(10)
        self.init_sensors()
        asyncio.create_task(self.connect_async())    
        LOG.info("Chain2Gate correctly initialized: %s", self.id)
    
    async def connect_async(self):
        while self._running:
            async with websockets.connect(self.ws_url) as ws:
                self._ws = ws
                while self._running:
                    msg = await ws.recv()
                    await self.process_message(msg)
            LOG.warning("Chain2Gate connection lost: %s", self.id)
            LOG.warning("Retrying in 10 seconds...")
            await asyncio.sleep(10)

    async def process_message(self, msg):
        msg = json.loads(msg)
        if "Chain2Data" in msg:
            msg = msg["Chain2Data"]
            if msg["Type"] == "CF1": # trama quartoraria
                LOG.info("Chain2Gate message received CF1 frame")
                await self.sens_tariff_code.set_value(msg["Payload"]["TariffCode"])
                await self.sens_curr_quart_act_energy.set_value(msg["Payload"]["CurrQuartActEnergy"])
                await self.sens_instant_power.set_value(msg["Payload"]["InstantPower"])
                await self.sens_quart_average_power.set_value(msg["Payload"]["QuartAveragePower"])
                await self.sens_total_act_energy.set_value(msg["Payload"]["TotalActEnergy"])
            elif msg["Type"] == "CF21": # trama superamento 300 W
                LOG.info("Chain2Gate message received CF21 frame")
                await self.sens_instant_power.set_value(msg["Payload"]["InstantPower"])
            else:
                LOG.warning("Chain2Gate message received %s frame", msg["Type"])
        elif "Chain2Info" in msg:
            pass
        
    def init_sensors(self):
        if not self._has_sensors:
            self.sens_tariff_code = C2GSensor("Tariff Code")
            self.sens_curr_quart_act_energy = C2GSensor("Curr Quart Act Energy", UnitOfEnergy.WATT_HOUR, SensorDeviceClass.ENERGY)
            self.sens_instant_power = C2GSensor("Instant Power", UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT)
            self.sens_quart_average_power = C2GSensor("Quart Average Power", UnitOfPower.WATT, SensorDeviceClass.POWER)
            self.sens_total_act_energy = C2GSensor("Total Act Energy", UnitOfEnergy.WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING)
            self._has_sensors = True
    
    def get_sensors(self):
        self.init_sensors()
        return [self.sens_tariff_code,
                self.sens_curr_quart_act_energy,
                self.sens_instant_power,
                self.sens_quart_average_power,
                self.sens_total_act_energy]
        
class C2GSensor:
    def __init__(self, name: str, unit: str = None, device_class: str = None, state_class: str = None):
        self.name = name
        self.value = None
        self.unit_of_measurement = unit
        self.device_class = device_class
        self.state_class = state_class

    async def set_value(self, value):
        self.value = value
        if self._callback:
            await self._callback()

    def set_callback(self, callback):
        self._callback = callback