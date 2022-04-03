import RPi.GPIO as GPIO
import time
import logging

class CarControl:
    #Car Motor PIN
    IN1 = 20
    IN2 = 21
    IN3 = 19
    IN4 = 26
    ENA = 16
    ENB = 13

    #Car Input Key PIN
    key = 8

    #UltraSonic PIN
    EchoPin = 0
    TrigPin = 1

    #RGB Light PIN
    LED_R = 22
    LED_G = 27
    LED_B = 24

    #UltraSonic Servo PIN
    UltraSonic_ServoPin = 23

    #Avoid Sensor PIN
    AvoidSensorLeft = 12
    AvoidSensorRight = 17

        
    def __init__(self, speed) -> None:
        self.speed = speed
        pass

    def init(self):
        logging.info("start initing car control, speed: %s", self.speed)
        #Set GPIO as BCM Mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)    

        #Motor PIN as output mode
        #Key PIN as input mode
        #UltraSonic, RGB Light,Servo PIN init
        #Avoid Sensor init
        GPIO.setup(self.ENA,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(self.IN1,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.IN2,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.ENB,GPIO.OUT,initial=GPIO.HIGH)
        GPIO.setup(self.IN3,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.IN4,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.key,GPIO.IN)
        GPIO.setup(self.EchoPin,GPIO.IN)
        GPIO.setup(self.TrigPin,GPIO.OUT)
        GPIO.setup(self.LED_R, GPIO.OUT)
        GPIO.setup(self.LED_G, GPIO.OUT)
        GPIO.setup(self.LED_B, GPIO.OUT)
        GPIO.setup(self.UltraSonic_ServoPin, GPIO.OUT)
        GPIO.setup(self.AvoidSensorLeft,GPIO.IN)
        GPIO.setup(self.AvoidSensorRight,GPIO.IN)

        #Set pwm PIN and frequency at 2000hz
        self.pwm_ENA = GPIO.PWM(self.ENA, 2000)
        self.pwm_ENB = GPIO.PWM(self.ENB, 2000)
        self.pwm_ENA.start(0)
        self.pwm_ENB.start(0)
        
        #Set UltraSonic Servo frequency and init duty cycle
        self.pwm_ultrasonic_servo = GPIO.PWM(self.UltraSonic_ServoPin, 50)
        self.pwm_ultrasonic_servo.start(0)

        time.sleep(2)
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 90)
        logging.info("complete initing car control")

    #Move Forward	
    def run(self, leftspeed, rightspeed):
        logging.info("move forward with speed: %s, %s", leftspeed, rightspeed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #Move Backward
    def back(self, leftspeed, rightspeed):
        logging.info("back with speed: %s, %s", leftspeed, rightspeed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)
        
    #Turn Left	
    def left(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #Turn Right
    def right(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)
        
    #Spin Left
    def spin_left(self, leftspeed, rightspeed):
        logging.debug("spin left with speed: %s, %s", leftspeed, rightspeed)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #Spin Right
    def spin_right(self, leftspeed, rightspeed):
        logging.debug("spin right with speed: %s, %s", leftspeed, rightspeed)
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #Break
    def brake(self):
        logging.debug("break")
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)

    #Key Test
    def key_scan(self):
        while GPIO.input(self.key):
            pass
        while not GPIO.input(self.key):
            time.sleep(0.01)
            if not GPIO.input(self.key):
                time.sleep(0.01)
                while not GPIO.input(self.key):
                    pass
                    
    #UltraSonic Distance Test
    def Distance_test(self):
        GPIO.output(self.TrigPin,GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(self.TrigPin,GPIO.LOW)
        while not GPIO.input(self.EchoPin):
            pass
        t1 = time.time()
        while GPIO.input(self.EchoPin):
            pass
        t2 = time.time()
        print("distance is %d " % (((t2 - t1)* 340 / 2) * 100))
        time.sleep(0.01)
        return ((t2 - t1)* 340 / 2) * 100
    
    def face_obstacle(self, distance_threshold):
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 90)
        time.sleep(0.8)
        frontdistance = self.Distance_test()
        return frontdistance < distance_threshold

    #Rotate Servo to position
    def servo_appointed_detection(self, pwm_servo, pos):
        for i in range(18):
            pwm_servo.ChangeDutyCycle(2.5 + 10 * pos/180)	
            
    def alert_no_target(self):
        GPIO.output(self.LED_R, GPIO.LOW)
        GPIO.output(self.LED_G, GPIO.LOW)
        GPIO.output(self.LED_B, GPIO.LOW)

    def alert_find_target(self):
        GPIO.output(self.LED_R, GPIO.LOW)
        GPIO.output(self.LED_G, GPIO.HIGH)
        GPIO.output(self.LED_B, GPIO.LOW)


    def alert_close_to_target(self):
        GPIO.output(self.LED_R, GPIO.HIGH)
        GPIO.output(self.LED_G, GPIO.LOW)
        GPIO.output(self.LED_B, GPIO.LOW)

    #Use UltraSonic to avoid obstace
    def servo_color_carstate(self):
        #RED Light
        GPIO.output(self.LED_R, GPIO.HIGH)
        GPIO.output(self.LED_G, GPIO.LOW)
        GPIO.output(self.LED_B, GPIO.LOW)
        self.back(20, 20)
        time.sleep(0.08)
        self.brake()
        
        #Servo to right (0 degree), test distance
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 0)
        time.sleep(0.8)
        rightdistance = self.Distance_test()
    
        #Servo to left (180 degree), test distance
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 180)
        time.sleep(0.8)
        leftdistance = self.Distance_test()

        #Servo to front (90 degree), test distance
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 90)
        time.sleep(0.8)
        frontdistance = self.Distance_test()
    
        if leftdistance < 30 and rightdistance < 30 and frontdistance < 30:
            #Turn around
            GPIO.output(self.LED_R, GPIO.HIGH)
            GPIO.output(self.LED_G, GPIO.LOW)
            GPIO.output(self.LED_B, GPIO.HIGH)
            self.spin_right(85, 85)
            time.sleep(0.58)
        elif leftdistance >= rightdistance:
            #Turn left
            GPIO.output(self.LED_R, GPIO.LOW)
            GPIO.output(self.LED_G, GPIO.LOW)
            GPIO.output(self.LED_B, GPIO.HIGH)
            self.spin_left(85, 85)
            self.time.sleep(0.28)
        elif leftdistance <= rightdistance:
            #Turn right
            GPIO.output(self.LED_R, GPIO.HIGH)
            GPIO.output(self.LED_G, GPIO.LOW)
            GPIO.output(self.LED_B, GPIO.HIGH)
            self.spin_right(85, 85)
            time.sleep(0.28)

