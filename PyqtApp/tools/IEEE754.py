import struct 
import binascii	

def float_to_hex16(f):
    hex_str = hex(struct.unpack('<I', struct.pack('<f', f))[0])[2:] 
    hex_str = '0'*(len(hex_str)%2) + hex_str
    # print('hex', hex_str)
    return binascii.unhexlify(hex_str)

def hex16_to_float(h:bytes):
    return struct.unpack('>f', h)[0]


if __name__ == "__main__":
    h = float_to_hex16(-0.71)
    print(h)
    print(hex16_to_float(h))
    
    
    