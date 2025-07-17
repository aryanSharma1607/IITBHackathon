from machine import I2C, Pin
from time import sleep
import math

MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

i2c = I2C(0, scl=Pin(5), sda=Pin(4))

i2c.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')

led = Pin(25, Pin.OUT)

lastN = 50 
pitch_history = []
imuCheck = False
capOff = True  
pitchChange = 20

def read_raw_data(addr):
    high = i2c.readfrom_mem(MPU6050_ADDR, addr, 1)[0]
    low = i2c.readfrom_mem(MPU6050_ADDR, addr + 1, 1)[0]
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

def get_pitch_angle(accel_x, accel_y, accel_z):
    pitch = math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)) * 57.2958
    return abs(pitch)

while True:

    accel_x = read_raw_data(ACCEL_XOUT_H) / 16384.0
    accel_y = read_raw_data(ACCEL_XOUT_H + 2) / 16384.0
    accel_z = read_raw_data(ACCEL_XOUT_H + 4) / 16384.0

    pitch = get_pitch_angle(accel_x, accel_y, accel_z)

    
    pitch_history.append(pitch)
    if len(pitch_history) > lastN:
        pitch_history.pop(0)

    if capOff:
        if len(pitch_history) == lastN:
            if abs(pitch - pitch_history[0]) > pitchChange:
                imuCheck = True
    else:
        imuCheck = False

    print("Pitch:", pitch, "capOff:", capOff, "imuCheck:", imuCheck)

    if 45 <= pitch <= 60 and accel_z > 0.2:
        led.value(1)
    else:
        led.value(0)

    sleep(0.1)
