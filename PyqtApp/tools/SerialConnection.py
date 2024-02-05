import serial

class SerialConnection:
    instance = None
    
    def __init__(self, ser:serial.Serial):
        self.ser = ser
    
    @classmethod
    def setInstance(cls, ser):
        cls.instance = SerialConnection(ser)
    
    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            return None
        return cls.instance
        