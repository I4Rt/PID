import serial 

class ConnectionHolder:
    __instance = None
    
    def __init__(self, com:str):
        self.comName = com
        self.connection = None
        self.isConnected = False
        try: 
            baudrate = 19200 
            self.connection = serial.Serial(com, baudrate=baudrate, timeout=0.1, parity='E')
            self.connection.flush()
            self.isConnected = True
        except Exception as e:
            pass
        
    @classmethod
    def changePort(cls, com:str):
        if cls.__instance:
            try:
                if cls.__instance.connection:
                    cls.__instance.connection.close()
                    cls.__instance.connection = None
            except Exception as e:
                print('change port exveption', e)
        cls.__instance = ConnectionHolder(com)
        
    @classmethod
    def getConnection(cls):
        if cls.__instance:
            return cls.__instance.connection
        
    @classmethod
    def getComName(cls):
        if cls.__instance:
            return cls.__instance.comName
        
    @classmethod 
    def getAvaliableComs(cls):
        res = []
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            res.append([port, desc])
        return res