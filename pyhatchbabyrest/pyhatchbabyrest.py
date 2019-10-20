import time

from enum import IntEnum

import pygatt


class PyHatchBabyRestSound(IntEnum):
    none = 0
    stream = 2
    noise = 3
    dryer = 4
    ocean = 5
    wind = 6
    rain = 7
    bird = 9
    crickets = 10
    brahms = 11
    twinkle = 13
    rockabye = 14


class PyHatchBabyRest(object):
    COLOR_GRADIENT = (254, 254, 254)  # setting this color turns on Gradient mode

    def __init__(self, addr=None):
        self.adapter = pygatt.GATTToolBackend()
        self.adapter.start()

        if addr is None:
            devices = self.adapter.scan()

            for device in devices:
                if device["address"][:8] == "F3:53:11":
                    addr = device["address"]
                    break
            else:
                raise RuntimeException(
                    "No address provided and could not find device via scan."
                )

        self.device = self.adapter.connect(
            addr, address_type=pygatt.BLEAddressType.random
        )

        self._char_tx = "02240002-5efd-47eb-9c1a-de53f7a2b232"
        self._char_feedback = "02260002-5efd-47eb-9c1a-de53f7a2b232"

        self._refresh_data()

    def _send_command(self, command):
        self.device.char_write(self._char_tx, bytearray(command, "utf-8"))
        time.sleep(0.25)
        self._refresh_data()

    def _refresh_data(self):
        response = [hex(x) for x in self.device.char_read(self._char_feedback)]

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
        self.power = not bool(int("11000000", 2) & int(response[14], 16))

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

    def set_color(self, red, green, blue, rgb=None):
        self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(red, green, blue, self.brightness)
        self._send_command(command)

    def set_brightness(self, brightness):
        self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(
            self.color[0], self.color[1], self.color[2], brightness
        )
        self._send_command(command)

    @property
    def connected(self):
        return self.device._connected
