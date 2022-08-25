import asyncio
from typing import Optional
from typing import Union

from bleak import BleakClient
from bleak import BleakScanner
from bleak.backends.device import BLEDevice

from .constants import BT_MANUFACTURER_ID
from .constants import CHAR_FEEDBACK
from .constants import CHAR_TX
from .constants import PyHatchBabyRestSound


class PyHatchBabyRestAsync(object):
    """An asynchronous interface to a Hatch Baby Rest device using bleak."""

    def __init__(
        self,
        address_or_ble_device: Union[str, BLEDevice, None] = None,
        scanner: Optional[BleakScanner] = None,
    ):
        loop = asyncio.get_event_loop()
        scanner = BleakScanner() if scanner is None else scanner

        if not address_or_ble_device:
            device = loop.run_until_complete(
                scanner.find_device_by_filter(
                    lambda device, _: BT_MANUFACTURER_ID
                    in device.metadata["manufacturer_data"].keys()
                )
            )
        elif isinstance(address_or_ble_device, BLEDevice):
            device = address_or_ble_device
        else:
            device = loop.run_until_complete(
                scanner.find_device_by_address(address_or_ble_device)
            )

        if device is None:
            raise RuntimeError(
                "No address or BLEDevice provided and could not find device via scan."
            )

        self.device = device

        loop.run_until_complete(self._refresh_data())

    async def _send_command(self, command: str):
        """Send a command do the device.

        :param command: The command to send.
        """
        async with BleakClient(self.device) as client:
            await client.write_gatt_char(
                char_specifier=CHAR_TX,
                data=bytearray(command, "utf-8"),
                response=True,
            )
        await asyncio.sleep(0.25)
        await self._refresh_data()

    async def _refresh_data(self):
        async with BleakClient(self.device) as client:
            raw_char_read = await client.read_gatt_char(CHAR_FEEDBACK)

        response = [hex(x) for x in raw_char_read]

        # Make sure the data is where we think it is
        assert response[5] == "0x43"  # color
        assert response[10] == "0x53"  # audio
        assert response[13] == "0x50"  # power

        red, green, blue, brightness = [int(x, 16) for x in response[6:10]]

        sound = PyHatchBabyRestSound(int(response[11], 16))

        volume = int(response[12], 16)

        power = not bool(int("11000000", 2) & int(response[14], 16))

        self.color = (red, green, blue)
        self.brightness = brightness
        self.sound = sound
        self.volume = volume
        self.power = power

    async def disconnect(self):
        async with BleakClient(self.device) as client:
            return await client.disconnect()

    async def power_on(self):
        command = "SI{:02x}".format(1)
        await self._send_command(command)

    async def power_off(self):
        command = "SI{:02x}".format(0)
        await self._send_command(command)

    async def set_sound(self, sound):
        command = "SN{:02x}".format(sound)
        return await self._send_command(command)

    async def set_volume(self, volume):
        command = "SV{:02x}".format(volume)
        return await self._send_command(command)

    async def set_color(self, red, green, blue):
        await self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(red, green, blue, self.brightness)
        return await self._send_command(command)

    async def set_brightness(self, brightness):
        await self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(
            self.color[0], self.color[1], self.color[2], brightness
        )
        return await self._send_command(command)

    @property
    async def connected(self):
        async with BleakClient(self.device) as client:
            return client.is_connected

    @property
    def name(self):
        return self.device.name
