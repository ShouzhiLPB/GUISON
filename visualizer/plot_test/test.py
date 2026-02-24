import struct

import serial

ser = serial.Serial("/dev/ttyACM0", 1000000)

while True:
    data = ser.read(4)

    if len(data) == 4:
        left, right = struct.unpack("<hh", data)
        print(left, right)
