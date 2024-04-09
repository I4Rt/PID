from tools.plant.Motor import *
from tools.plant.PowerSupply import *
from tools.plant.Heater import *
from tools.plant.VoltageGetter import *
from tools.plant.ThermoGetter import *

motorRotate = Motor(b'\x04')
motorVertical = Motor(b'\x03')

powerSupply = PowerSupply(b'\x05')

heater = Heater(b'\x01')

voltageGetter = VoltageGetter(b'\x01')

thermoCoupleMainGetter = ThermoGetter(b'\x02', b'\x00\x00')
thermoCoupleOuterGetter = ThermoGetter(b'\x02', b'\x00\x06')