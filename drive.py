#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_LED = 14
GPIO_SERVO = 17

#set up control pins for motor driver
STBY = 12
AIN1 = 13
AIN2 = 19
PWMA = 26
BIN1 = 21
BIN2 = 20
PWMB = 16


#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_LED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GPIO_SERVO, GPIO.OUT)

# motor driver init
GPIO.setup(STBY, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)

#set initial condiions, STBY
#is low, so no motors running
GPIO.output(STBY, GPIO.LOW)

GPIO.output(AIN1, GPIO.HIGH)
GPIO.output(AIN2, GPIO.LOW)
GPIO.output(PWMA, GPIO.HIGH)

GPIO.output(BIN1, GPIO.HIGH)
GPIO.output(BIN2, GPIO.LOW)
GPIO.output(PWMB, GPIO.HIGH)

# servo init
servo = GPIO.PWM(GPIO_SERVO, 50) # 50Hz
servo.start(2.5)

left = GPIO.PWM(PWMA, 50)
right = GPIO.PWM(PWMB, 50)
init_speed = 50
speed = init_speed
left.start(speed)
right.start(speed)

#movement is governed by the 4
#following functions.  These will
#go into their own library, ultimately.
def go_forward(speed):
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)

#    pa.ChangeDutyCycle(speed) 
#    pb.ChangeDutyCycle(speed) 

    GPIO.output(STBY, GPIO.HIGH) #start

def turn_left(run_time):
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)

    GPIO.output(STBY, GPIO.HIGH) #start

def turn_right(run_time):
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)

    GPIO.output(STBY, GPIO.HIGH) #start

def go_back(run_time):
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)

    GPIO.output(STBY, GPIO.HIGH) #start

def change_speed(speed):
    left.ChangeDutyCycle(speed)
    right.ChangeDutyCycle(speed)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    led_status = "unknown"
    try:
        while True:
            dist = distance()
            print ("Distance = %.1f cm" % dist, "speed = ", speed, "led = ", led_status)
            if int(dist) < 50:
                led_status = "on"
                GPIO.output(GPIO_LED, GPIO.HIGH) # Turn on LED
                for dc in range(speed, 10, -4):
                    change_speed(dc)
                    time.sleep(0.1)
                    speed = dc
                GPIO.output(STBY, GPIO.LOW) #stop motor
                time.sleep(2)
                change_speed(30)
                go_back(0.2)
                time.sleep(1)
                turn_left(0.1)
            else:
                led_status = "off"
                GPIO.output(GPIO_LED, GPIO.LOW) # Turn off LED
                if speed != init_speed:
                    for dc in range(speed, init_speed, 2):
                        change_speed(dc)
                        time.sleep(0.1)
                        speed = dc

                #servo.ChangeDutyCycle(2.5)
                go_forward(speed)
                
            time.sleep(0.2)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
