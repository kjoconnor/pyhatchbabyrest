# Hatch Baby Rest Python Bindings
This library will allow you to control a [Hatch Baby Rest device](https://www.hatchbaby.com/rest) (note, /not/ the Hatch Baby Rest+, which is Wi-Fi enabled) over [BLE](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy).

## Requirements
This was tested on a Raspberry Pi 3 Model B Rev 1.2, but should work on any Unix system that is compatible with the `GATTToolBackend` of [pygatt](https://github.com/peplin/pygatt).

## Installation
`pip install pyhatchbabyrest`

## Examples
```python3
In [1]: from pyhatchbabyrest import PyHatchBabyRest, PyHatchBabyRestSound

In [2]: rest = PyHatchBabyRest()

In [3]: rest.power
Out[3]: False

In [4]: rest.power_on()

In [5]: rest.volume
Out[5]: 30

In [6]: rest.set_volume(10)

In [7]: rest.volume
Out[7]: 10

In [8]: rest.set_color(255, 0, 0)

In [9]: rest.color
Out[9]: (255, 0, 0)

In [10]: rest.set_brightness(100)

In [11]: rest.set_sound(PyHatchBabyRestSound.stream)

In [12]: rest.sound
Out[12]: <PyHatchBabyRestSound.stream: 2>

In [13]: rest.set_color(*PyHatchBabyRest.COLOR_GRADIENT)
    
In [14]: rest.connected
Out[14]: True

In [15]: rest.disconnect()

In [16]: rest.connected
Out[16]: False
```

## Credits
Huge thanks to @Marcus-L for their repo at [GitHub - Marcus-L/m4rcus.HatchBaby.Rest: Control Hatch Baby Rest devices using Bluetooth LE](https://github.com/Marcus-L/m4rcus.HatchBaby.Rest) which did all the hard work of finding the right characteristics, commands, etc.