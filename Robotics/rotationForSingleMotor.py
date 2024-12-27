from time import sleep
import RPi.GPIO as gpio

def degreesToSteps(angle):
    stepsPerRevolution = 6400
    steps = float((angle / 360.0) * stepsPerRevolution)
    return int(steps)

direction_pin = 20
pulse_pin = 21
cw_direction = 0
ccw_direction = 1

gpio.setmode(gpio.BCM)
gpio.setup(direction_pin, gpio.OUT)
gpio.setup(pulse_pin, gpio.OUT)
gpio.output(direction_pin, cw_direction)

try:
    while True:
        angle = float(input('Enter degrees: '))
        print('Direction CW')
        sleep(.5)
        gpio.output(direction_pin, cw_direction)
        for x in range(degreesToSteps(angle)):
            gpio.output(pulse_pin, gpio.HIGH)
            sleep(.00001)
            gpio.output(pulse_pin, gpio.LOW)
            sleep(.00001)

except KeyboardInterrupt:
    gpio.cleanup()
