#Libraries
import RPi.GPIO as GPIO
import time

surountdings_cm = {}
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins

# RED ligth
RED_LED = 14
GPIO.setup(RED_LED, GPIO.OUT, initial=GPIO.HIGH)

# Distance sensor 1 
SONIC1_TRIGGER = 18
GPIO.setup(SONIC1_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
SONIC1_ECHO = 24
GPIO.setup(SONIC1_ECHO, GPIO.IN)
time.sleep(2)

# # Distance sensor 2
SONIC2_TRIGGER = 22
GPIO.setup(SONIC2_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
SONIC2_ECHO = 25
GPIO.setup(SONIC2_ECHO, GPIO.IN)
time.sleep(2)

# servo motor controling sonic sensor2
SERVO_SONIC2 = 17
GPIO.setup(SERVO_SONIC2, GPIO.OUT)
# servo init
servo = GPIO.PWM(SERVO_SONIC2, 50) # 50Hz
servo.start(0)

#set up control pins for motor driver
MOTOR_STBY = 12
GPIO.setup(MOTOR_STBY, GPIO.OUT, initial=GPIO.LOW)

# Motor A on LEFT
MOTOR_A_IN1 = 13
GPIO.setup(MOTOR_A_IN1, GPIO.OUT)
GPIO.output(MOTOR_A_IN1, GPIO.HIGH)

MOTOR_A_IN2 = 19
GPIO.setup(MOTOR_A_IN2, GPIO.OUT)
GPIO.output(MOTOR_A_IN2, GPIO.LOW)

MOTOR_A_PWM = 26
GPIO.setup(MOTOR_A_PWM, GPIO.OUT)
GPIO.output(MOTOR_A_PWM, GPIO.HIGH)
left = GPIO.PWM(MOTOR_A_PWM, 50)

# Motor B on RIGHT
MOTOR_B_IN1 = 21
GPIO.setup(MOTOR_B_IN1, GPIO.OUT)
GPIO.output(MOTOR_B_IN1, GPIO.HIGH)

MOTOR_B_IN2 = 20
GPIO.setup(MOTOR_B_IN2, GPIO.OUT)
GPIO.output(MOTOR_B_IN2, GPIO.LOW)

MOTOR_B_PWM = 16
GPIO.setup(MOTOR_B_PWM, GPIO.OUT)
GPIO.output(MOTOR_B_PWM, GPIO.HIGH)
right = GPIO.PWM(MOTOR_B_PWM, 50)


init_speed = 60
speed = init_speed
left.start(init_speed+4)
right.start(init_speed)


def stop(speed):
    GPIO.output(RED_LED, GPIO.HIGH) # Turn on LED
    # slow down and stop
    stop_status = GPIO.input(MOTOR_STBY)
    #print("stop_status = " + str(stop_status))
    if stop_status == 1:
        for step in range(speed, 30, -10):
            print("slowing down, current speed = " + str(step))
            change_speed(step)
            time.sleep(0.1)
            speed = step
    
        GPIO.output(MOTOR_STBY, GPIO.LOW) #stop motor
        #stop_status = GPIO.input(MOTOR_STBY)
        #print("stopped status = " + str(stop_status))
        return speed
    else:
        print("already stopped! skipping stop instruction.")

def speedup(speed):
    GPIO.output(RED_LED, GPIO.HIGH) # Turn off LED
    for step in range(speed, init_speed,10):
        print("speeding up, current speed = " + str(step))
        change_speed(step)
        time.sleep(0.1)
        speed = step
    change_speed(init_speed)
    return speed

def change_speed(speed):
    aligned_speed = speed + 4 # car is going more to the right, so lets align speed
    left.ChangeDutyCycle(aligned_speed)
    right.ChangeDutyCycle(speed)


# Movement of motors is controled by these 4 functions
def go_forward():
    GPIO.output(MOTOR_A_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)
    GPIO.output(MOTOR_B_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN2, GPIO.LOW)
    GPIO.output(MOTOR_STBY, GPIO.HIGH) #start

def go_back():
    #GPIO.output(RED_LED, GPIO.HIGH) # Turn on LED
    GPIO.output(MOTOR_A_IN1, GPIO.LOW)
    GPIO.output(MOTOR_A_IN2, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN1, GPIO.LOW)
    GPIO.output(MOTOR_B_IN2, GPIO.HIGH)
    GPIO.output(MOTOR_STBY, GPIO.HIGH) #start

def turn_left():
    GPIO.output(MOTOR_A_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)
    GPIO.output(MOTOR_B_IN1, GPIO.LOW)
    GPIO.output(MOTOR_B_IN2, GPIO.LOW)
    GPIO.output(MOTOR_STBY, GPIO.HIGH) #start

def turn_right():
    GPIO.output(MOTOR_A_IN1, GPIO.LOW)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)
    GPIO.output(MOTOR_B_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN2, GPIO.LOW)
    GPIO.output(MOTOR_STBY, GPIO.HIGH) #start


# Mesure the distance of object in front of sonic sensors
def measure_distance(trigger_pin, echo_pin):

    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    while GPIO.input(echo_pin)==0:
        pulse_start_time = time.time()
    while GPIO.input(echo_pin)==1:
        pulse_end_time = time.time()
 
    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * 17150, 2)

    return distance
 

def Set_Sonic2_Angle(angle):
    duty = angle / 18 + 2
    GPIO.output(SERVO_SONIC2, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.3)
    GPIO.output(SERVO_SONIC2, False)
    servo.ChangeDutyCycle(0)
    
def is_too_close(distance):
    if distance < 10:
        change_speed(40)
        go_back()
        time.sleep(0.5)

def direction_lookup():
    # right
    Set_Sonic2_Angle(40)
    surountdings_cm['right'] = measure_distance(SONIC2_TRIGGER, SONIC2_ECHO)
    print ("right distance = " + str(surountdings_cm['right']))
    time.sleep(1.2)

    # front
    Set_Sonic2_Angle(90)
    surountdings_cm['front'] = measure_distance(SONIC2_TRIGGER, SONIC2_ECHO)
    print ("front distance = " + str(surountdings_cm['front']))
    is_too_close(surountdings_cm['front'])
    time.sleep(1.2)

    # left
    Set_Sonic2_Angle(150) 
    surountdings_cm['left'] = measure_distance(SONIC2_TRIGGER, SONIC2_ECHO)
    print ("left distance = " + str(surountdings_cm['left']))
    time.sleep(1.2)
    
    # at the end look back to the front
    Set_Sonic2_Angle(90)
    
    max_val = max(surountdings_cm.values())
    max_key = [k for k, v in surountdings_cm.items() if v == max_val]

    return surountdings_cm, max_key

if __name__ == '__main__':
    led_status = "unknown"
    try:
        while True:
            dist1 = measure_distance(SONIC1_TRIGGER, SONIC1_ECHO)
            dist2 = measure_distance(SONIC2_TRIGGER, SONIC2_ECHO)
            print("Distance down = %.1f cm" % dist1, "Distance up = %.1f cm" % dist2, "speed = %s" % speed, "red led = %s " % led_status)
            
            ## mind sensor error when reporting distance longer than 400cm (sensor ability)
            #if int(dist1) < 50 or int(dist2) < 10 or int(dist1) > 400: 
            if int(dist1) < 30 or int(dist2) < 20:    
                led_status = "on"
                print("stopping")
                stop(speed)

                print("deciding where to go")
                wheretogo = direction_lookup()
                print(wheretogo[0])
                print(wheretogo[1])
                
                for direction in wheretogo[1]:
                    time_to_turn = 0.8
                    if speed < 31:
                        print("changing speed, i'm too slow")
                        change_speed(init_speed)
                    
                    if int(dist2) < 20 or int(dist1) < 20:
                        print("go back")
                        change_speed(50)
                        go_back()
                        time.sleep(2)
                        stop(speed)
                        direction_lookup()
                    
                    if direction == "left":
                        print("go left, speed: %s " % speed)
                        turn_left()
                        time.sleep(time_to_turn)
                    elif direction == "right":
                        print("go right")
                        turn_right()
                        time.sleep(time_to_turn)
                    elif direction == "front":
                        print("go forward")
                        go_forward()
                        time.sleep(time_to_turn)
                    else:
                        print("chyba, kontroluji znovu")
                        direction_lookup()
                print("current speed: " + str(speed))
                speedup(speed)
                go_forward()
                

            else:
                GPIO.output(RED_LED, GPIO.LOW) # Turn off LED
                led_status = "off"
                if speed != init_speed:
                    print("i seems to be too slow, current speed: " + str(speed))
                    speedup(speed)
                go_forward()

            time.sleep(0.1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Executing stopped by User")
        servo.stop()
        GPIO.cleanup()
