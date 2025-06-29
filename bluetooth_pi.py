import serial

ser = serial.Serial('/dev/rfcomm0',9600)

print("Waiting for request...")

while True:
    line = ser.readline().decode('utf-8').strip()
    print(f"Received:{line}")
    
    if line == "REQHPCRP1":
        response = "U:6600, OK\n"
        ser.write(response.encode('utf-8'))
        print("Sent response to PC")
    else:
        print("Unknown request")