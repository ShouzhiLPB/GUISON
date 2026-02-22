import serial
import struct

ser = serial.Serial('/dev/tty.usbmodem158410201', 1000000)

while True:
    data = ser.read(4)

    if len(data) == 4:
        left, right = struct.unpack('<hh', data)
        print(left, right)
