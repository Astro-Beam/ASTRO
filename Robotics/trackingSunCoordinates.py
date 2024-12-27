import RPi.GPIO as gpio
from time import sleep
from astropy.coordinates import get_sun, AltAz, EarthLocation
from astropy.time import Time

d_pin_1 = 20
p_pin_1 = 21
d_pin_2 = 19
p_pin_2 = 26

cw_direction = 0 
ccw_direction = 1

steps_per_revolution = 6400

telescope_location = EarthLocation(lat=39.127, lon=25.8, height=50)
altaz_frame = AltAz(location=telescope_location)

gpio.setmode(gpio.BCM)
gpio.setup(d_pin_1, gpio.OUT)
gpio.setup(p_pin_1, gpio.OUT)
gpio.setup(d_pin_2, gpio.OUT)
gpio.setup(p_pin_2, gpio.OUT)

def move_motor(pin_dir, pin_pulse, direction, steps):
    gpio.output(pin_dir, direction)
    for _ in range(steps):
        gpio.output(pin_pulse, gpio.HIGH)
        sleep(0.001)  # Adjust speed
        gpio.output(pin_pulse, gpio.LOW)
        sleep(0.001)


def automatic_tracking():
    print("Automatic tracking active.")
    try:
        while True:
            current_time = Time.now()
            sun_position = get_sun(current_time).transform_to(altaz_frame)
            target_alt = sun_position.alt.degree
            target_az = sun_position.az.degree
            alt_steps = int((steps_per_revolution / 360) * target_alt)
            az_steps = int((steps_per_revolution / 360) * target_az)
            move_motor(d_pin_1, p_pin_1, cw_direction if alt_steps > 0 else ccw_direction, abs(target_alt))
            move_motor(d_pin_2, p_pin_2, cw_direction if az_steps > 0 else ccw_direction, abs(target_az))
            
            sleep(1)  # Adjust update frequency

    except KeyboardInterrupt:
        gpio.cleanup()
try:
    while True:
        # manual_control()
        automatic_tracking()

except KeyboardInterrupt:
    gpio.cleanup()
