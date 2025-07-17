from machine import I2C, Pin, ADC
from time import sleep
import math

# MPU6050 Setup
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
i2c.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')

# Hall Effect Setup
hall_sensor = ADC(Pin(26))
MAGNET_THRESHOLD = 45000

# Hardware Setup
led = Pin(25, Pin.OUT)

# IMU Variables
lastN = 50 
pitch_history = []
imuCheck = False
capOff = True  
pitchChange = 20

# Sip Counter
sips_count = 0

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

def check_magnet():
    adc_value = hall_sensor.read_u16()
    return adc_value > MAGNET_THRESHOLD

print("Smart Bottle Monitor Starting...")
print("Cap on = magnet close, Cap off = magnet far")

try:
    while True:
        # Read hall effect sensor
        magnet_detected = check_magnet()
        
        # Update capOff based on magnet detection
        # When magnet is close (cap on) -> capOff = False
        # When magnet is far (cap off) -> capOff = True
        capOff = not magnet_detected
        
        # Read IMU data
        accel_x = read_raw_data(ACCEL_XOUT_H) / 16384.0
        accel_y = read_raw_data(ACCEL_XOUT_H + 2) / 16384.0
        accel_z = read_raw_data(ACCEL_XOUT_H + 4) / 16384.0
        pitch = get_pitch_angle(accel_x, accel_y, accel_z)
        
        # Update pitch history
        pitch_history.append(pitch)
        if len(pitch_history) > lastN:
            pitch_history.pop(0)
        
        # Check for drinking motion when cap is off
        if capOff:
            if len(pitch_history) == lastN:
                if abs(pitch - pitch_history[0]) > pitchChange:
                    imuCheck = True
        else:
            # When cap is put back on (magnet close), complete the cycle
            if imuCheck:
                sips_count += 1
                print(f"🥤 SIP DETECTED! Total sips: {sips_count}")
                imuCheck = False
        
        # LED control for tilt detection
        if 45 <= pitch <= 60 and accel_z > 0.2:
            led.value(1)
        else:
            led.value(0)
        
        # Status display
        cap_status = "ON" if not capOff else "OFF"
        drinking_status = "DRINKING MOTION" if imuCheck else "READY"
        
        print(f"Cap: {cap_status} | Pitch: {pitch:.1f}° | Status: {drinking_status} | Sips: {sips_count}")
        
        sleep(0.1)

except KeyboardInterrupt:
    print(f"\nStopped. Total sips consumed: {sips_count}")
    led.value(0)