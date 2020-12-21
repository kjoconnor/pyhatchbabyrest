import time

import pygatt  # type: ignore

from .constants import CHAR_TX, CHAR_FEEDBACK, PyHatchBabyRestSound


class PyHatchBabyRest(object):
    """ A synchronous interface to a Hatch Baby Rest device using pygatt. """
    def __init__(self, addr: str = None, adapter: pygatt.GATTToolBackend = None):
        """ Instantiate the interface.

        :param addr: A specific address to connect to.
        :param adapter: An already instantiated `pygatt.GATTToolBackend`.
        """
        if adapter is None:
            self.adapter = pygatt.GATTToolBackend()
            self.adapter.start()
        else:
            self.adapter = adapter

        if addr is None:
            devices = self.adapter.scan()

            for device in devices:
                if device["address"][:8] == "F3:53:11":
                    addr = device["address"]
                    break
            else:
                raise RuntimeError(
                    "No address provided and could not find device via scan."
                )

        self.device = self.adapter.connect(
            addr, address_type=pygatt.BLEAddressType.random
        )

        self._refresh_data()

    def _send_command(self, command: str):
        """ Send a command to the device.

        :param command: The command to send.
        """
        self.device.char_write(CHAR_TX, bytearray(command, "utf-8"))
        time.sleep(0.25)
        self._refresh_data()

    def _refresh_data(self) -> None:
        """ Request updated data from the device and set the local attributes. """
        response = [hex(x) for x in self.device.char_read(CHAR_FEEDBACK)]

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

    def disconnect(self):
        return self.device.disconnect()

    def power_on(self):
        command = "SI{:02x}".format(1)
        self._send_command(command)

    def power_off(self):
        command = "SI{:02x}".format(0)
        self._send_command(command)

    def set_sound(self, sound):
        command = "SN{:02x}".format(sound)
        self._send_command(command)

    def set_volume(self, volume):
        command = "SV{:02x}".format(volume)
        self._send_command(command)

    def set_color(self, red: int, green: int, blue: int):
        self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(red, green, blue, self.brightness)
        self._send_command(command)

    def set_brightness(self, brightness: int):
        self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(
            self.color[0], self.color[1], self.color[2], brightness
        )
        self._send_command(command)

    @property
    def connected(self):
        return self.device._connected
