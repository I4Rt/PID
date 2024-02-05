import struct 
import binascii	

def float_to_hex16(f):
    return binascii.unhexlify(hex(struct.unpack('<I', struct.pack('<f', f))[0])[2:])

def hex16_to_float(h:bytes):
    return struct.unpack('>f', h)[0]


if __name__ == "__main__":
    h = float_to_hex16(3023.521)
    print(h)
    print(hex16_to_float(h))