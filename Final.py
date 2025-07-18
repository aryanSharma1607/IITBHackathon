from machine import I2C, Pin, ADC
from time import sleep
import time
import math

GREEN_TO_YELLOW_TIME = 0.15 # minutes
YELLOW_TO_RED_TIME = 0.3 # minutes

#imu setup
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
i2c.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')

# hall sensor
hall_sensor = ADC(Pin(26))
MAGNET_THRESHOLD = 45000

green_led = Pin(14, Pin.OUT)
yellow_led = Pin(13, Pin.OUT)
red_led = Pin(12, Pin.OUT)
buzzer = Pin(10, Pin.OUT)

# 555 IC
pulse_pin = Pin(15, Pin.IN)

lastN = 50 
pitch_history = []
imuCheck = False
capOff = True  
pitchChange = 20

sips_count = 0

pulse_count = 0
last_pulse_state = 0
target_pulses_yellow = GREEN_TO_YELLOW_TIME * 60
target_pulses_red = YELLOW_TO_RED_TIME * 60       

buzzer_duration = 3 # seconds

#LED States: 0=green, 1=yellow, 2=red
current_led_state = 0

def buzzer_trigger():
    global buzzer_duration
    buzzer.value(1)
    time.sleep(buzzer_duration)
    buzzer.value(0)

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

def update_leds():
    """Update LED states based on current_led_state"""
    global current_led_state
    
    green_led.value(0)
    yellow_led.value(0)
    red_led.value(0)
    
    if current_led_state == 0:      # Green state
        green_led.value(1)
        buzzer.value(0)
    elif current_led_state == 1:    # Yellow state
        yellow_led.value(1)
        buzzer.value(0)
    elif current_led_state == 2:    # Red state
        red_led.value(1)
        buzzer_trigger()

def reset_timer():
    """Reset timer and switch to green state"""
    global pulse_count, current_led_state
    pulse_count = 0
    current_led_state = 0
    update_leds()
    print("Timer reset - Green LED ON")

def check_timer():
    """Check timer pulses and update LED state accordingly"""
    global pulse_count, last_pulse_state, current_led_state
    
    current_pulse_state = pulse_pin.value()
    
    if last_pulse_state == 0 and current_pulse_state == 1:
        pulse_count += 1
        print(f"Pulse detected! Count: {pulse_count}") 
        
        if pulse_count >= target_pulses_red and current_led_state != 2:
            current_led_state = 2  # Red state
            update_leds()
            print(f"Red LED ON (Pulse: {pulse_count})")
        elif pulse_count >= target_pulses_yellow and current_led_state == 0:
            current_led_state = 1  # Yellow state
            update_leds()
            print(f"Yellow LED ON (Pulse: {pulse_count})")
    
    last_pulse_state = current_pulse_state

print("Smart Bottle Monitor Starting...")
print(f"Timings: Green->Yellow: {GREEN_TO_YELLOW_TIME}min, Yellow->Red: {YELLOW_TO_RED_TIME}min")
print("Cap on = magnet close, Cap off = magnet far")

# Initialize with green LED on
reset_timer()

try:
    while True:
        # Check timer pulses
        check_timer()
        
        #Read hall effect sensor
        magnet_detected = check_magnet()
        
        # Update capOff based on magnet detection
        capOff = not magnet_detected
        
        #Read IMU data
        accel_x = read_raw_data(ACCEL_XOUT_H) / 16384.0
        accel_y = read_raw_data(ACCEL_XOUT_H + 2) / 16384.0
        accel_z = read_raw_data(ACCEL_XOUT_H + 4) / 16384.0
        pitch = get_pitch_angle(accel_x, accel_y, accel_z)
        
        #Update pitch history
        pitch_history.append(pitch)
        if len(pitch_history) > lastN:
            pitch_history.pop(0)
        
        #Check for drinking motion when cap is off
        if capOff:
            if len(pitch_history) == lastN:
                if abs(pitch - pitch_history[0]) > pitchChange:
                    imuCheck = True
        else:
            # When cap is put back on (magnet close), complete the cycle
            if imuCheck:
                sips_count += 1
                print(f"SIP DETECTED! Total sips: {sips_count}")
                imuCheck = False
                
                # Reset timer and return to green state after any sip
                reset_timer()
        
        # Status display
        cap_status = "ON" if not capOff else "OFF"
        drinking_status = "DRINKING MOTION" if imuCheck else "READY"
        led_status = ["GREEN", "YELLOW", "RED"][current_led_state]
        
        print(f"Cap: {cap_status} | Pitch: {pitch:.1f}° | Status: {drinking_status} | LED: {led_status} | Timer: {pulse_count}s | Sips: {sips_count}")
        
        sleep(0.01) 
        
except KeyboardInterrupt:
    print(f"\nStopped. Total sips consumed: {sips_count}")
    green_led.value(0)
    yellow_led.value(0)
    red_led.value(0)
    buzzer.value(0)
