import serial
import time

if __name__ == "__main__":
    ser = serial.Serial("/dev/ttyACM0", 1000000, timeout=1)
    time.sleep(2)
    
    print("Reading from teensy :")
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").rstrip()
                print(f"Received : {line}")
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        ser.close()
        print("Port serial closed.")



