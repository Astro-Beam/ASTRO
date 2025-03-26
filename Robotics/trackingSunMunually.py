# import RPi.GPIO as gpio
# from time import sleep
import numpy as np
from datetime import datetime, timezone
from astropy.time import Time
from astropy.coordinates import get_sun

# d_pin_1 = 20
# p_pin_1 = 21
# d_pin_2 = 19
# p_pin_2 = 26

# cw_direction = 0 
# ccw_direction = 1

# steps_per_revolution = 6400

# telescope_location = EarthLocation(lat=39.127, lon=25.8, height=50)
# altaz_frame = AltAz(location=telescope_location)

# gpio.setmode(gpio.BCM)
# gpio.setup(d_pin_1, gpio.OUT)
# gpio.setup(p_pin_1, gpio.OUT)
# gpio.setup(d_pin_2, gpio.OUT)
# gpio.setup(p_pin_2, gpio.OUT)

# def move_motor(pin_dir, pin_pulse, direction, steps):
#     gpio.output(pin_dir, direction)
#     for _ in range(steps):
#         gpio.output(pin_pulse, gpio.HIGH)
#         sleep(0.001)  # Adjust speed
#         gpio.output(pin_pulse, gpio.LOW)
#         sleep(0.001)

def automatic_tracking_better():
    telescopeLongitude = 22.9638  
    telescopeLatitude = 40.6401   
    longitude_hours = telescopeLongitude / 15

    time = Time(datetime.utcnow())

    sun_coord = get_sun(time)
    print(sun_coord)
    rightAscension = sun_coord.ra.hour
    delta = np.radians(sun_coord.dec.deg)

    lst = time.sidereal_time('apparent', longitude_hours).hour
    # convert hours to degrees by multiplying by 15 and then to radians
    # we want to ensure HA remains within the range [-180°, +180°]:
    # add 180° to shift range from [-360°, 360°] to [0°, 540°]
    # take modulo 360° to keep it within [0°, 360°]
    # subtract 180° to shift range back to [-180°, +180°]
    hourAngle = ((lst - rightAscension) * 15 + 180) % 360 - 180
    
    latitudeRad = np.radians(telescopeLatitude)
    height = np.degrees(np.arcsin(np.sin(latitudeRad) * np.sin(delta) + np.cos(latitudeRad) * np.cos(delta) * np.cos(hourAngle)))

    # adjusted to start from South and increase clockwise)
    azimuth = (np.degrees(np.arctan2(np.sin(hourAngle), np.cos(latitudeRad) * np.tan(delta) - np.sin(latitudeRad) * np.cos(hourAngle))) + 180) % 360

    print(f"Sun's Right Ascension: {sun_coord.ra.to_string(unit='hourangle', precision=2)} ({sun_coord.ra.deg:.6f}°)")
    print(f"Sun's Declination: {sun_coord.dec.deg:.6f}°")
    print(f"Height (Altitude): {height:.2f}°")
    print(f"Azimuth: {azimuth:.2f}°")


try:
    # manual_control()
    automatic_tracking_better()

except KeyboardInterrupt:
        exit(0)
        #gpio.cleanup()


