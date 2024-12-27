from time import sleep
import RPi.GPIO as gpio

def degreesToSteps(angle):
    stepsPerRevolution = 6400
    steps = float((angle / 360.0) * stepsPerRevolution)
    return int(steps)

direction_pin1 = 20
pulse_pin1 = 21
direction_pin2 = 19
pulse_pin2 = 26
cw_direction = 0
ccw_direction = 1

gpio.setmode(gpio.BCM)
gpio.setup(direction_pin1, gpio.OUT)
gpio.setup(pulse_pin1, gpio.OUT)

gpio.setup(direction_pin2, gpio.OUT)
gpio.setup(pulse_pin2, gpio.OUT)

gpio.output(direction_pin1, cw_direction)
gpio.output(direction_pin2, cw_direction)

try:
    while True:
        angle = float(input('Enter degrees: '))
        print('Direction CW')
        sleep(.5)
        gpio.output(direction_pin1, cw_direction)
        gpio.output(direction_pin2, cw_direction)
        maxSteps = degreesToSteps(angle)
        for currentStep in range(maxSteps):
                gpio.output(pulse_pin1, gpio.HIGH)
                sleep(0.001)  # Adjust this to control motor speed
                gpio.output(pulse_pin1, gpio.LOW)
                gpio.output(pulse_pin2, gpio.HIGH)
                sleep(0.001)
                gpio.output(pulse_pin2, gpio.LOW)

except KeyboardInterrupt:
    gpio.cleanup()
