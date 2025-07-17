from machine import ADC, Pin
from time import sleep

# Setup ADC on GPIO 26
adc = ADC(Pin(26))

try:
    while True:
        # Read ADC value and convert to voltage
        adc_value = adc.read_u16()
        voltage = (adc_value / 65535) * 3.3
        
        print(adc_value)
        
        sleep(0.1)

except KeyboardInterrupt:
    print("Stopped")