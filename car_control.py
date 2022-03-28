import RPi.GPIO as GPIO
import time

class CarControl:
    #小车电机引脚定义
    IN1 = 20
    IN2 = 21
    IN3 = 19
    IN4 = 26
    ENA = 16
    ENB = 13

    #小车按键定义
    key = 8

    #超声波引脚定义
    EchoPin = 0
    TrigPin = 1

    #RGB三色灯引脚定义
    LED_R = 22
    LED_G = 27
    LED_B = 24

    #舵机引脚定义
    UltraSonic_ServoPin = 23

    #红外避障引脚定义
    AvoidSensorLeft = 12
    AvoidSensorRight = 17

        
    def __init__(self, speed) -> None:
        self.speed = speed
        pass

    def init(self):
        #设置GPIO口为BCM编码方式
        GPIO.setmode(GPIO.BCM)

        #忽略警告信息
        GPIO.setwarnings(False)    

        #电机引脚初始化为输出模式
        #按键引脚初始化为输入模式
        #超声波,RGB三色灯,舵机引脚初始化
        #红外避障引脚初始化

        # global pwm_ENA
        # global pwm_ENB
        # global pwm_servo
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
        #设置pwm引脚和频率为2000hz
        self.pwm_ENA = GPIO.PWM(self.ENA, 2000)
        self.pwm_ENB = GPIO.PWM(self.ENB, 2000)
        self.pwm_ENA.start(0)
        self.pwm_ENB.start(0)
        #设置舵机的频率和起始占空比
        self.pwm_ultrasonic_servo = GPIO.PWM(self.UltraSonic_ServoPin, 50)
        self.pwm_ultrasonic_servo.start(0)

        time.sleep(2)
        self.servo_appointed_detection(90)

    #小车前进	
    def run(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #小车后退
    def back(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)
        
    #小车左转	
    def left(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #小车右转
    def right(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)
        
    #小车原地左转
    def spin_left(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.IN3, GPIO.HIGH)
        GPIO.output(self.IN4, GPIO.LOW)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #小车原地右转
    def spin_right(self, leftspeed, rightspeed):
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.HIGH)
        self.pwm_ENA.ChangeDutyCycle(leftspeed)
        self.pwm_ENB.ChangeDutyCycle(rightspeed)

    #小车停止	
    def brake(self):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        GPIO.output(self.IN3, GPIO.LOW)
        GPIO.output(self.IN4, GPIO.LOW)

    #按键检测
    def key_scan(self):
        while GPIO.input(self.key):
            pass
        while not GPIO.input(self.key):
            time.sleep(0.01)
            if not GPIO.input(self.key):
                time.sleep(0.01)
                while not GPIO.input(self.key):
                    pass
                    
    #超声波函数
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
        
    #舵机旋转到指定角度
    def servo_appointed_detection(self, pwm_servo, pos):
        for i in range(18):
            pwm_servo.ChangeDutyCycle(2.5 + 10 * pos/180)	
            
    #舵机旋转超声波测距避障，led根据车的状态显示相应的颜色
    def servo_color_carstate(self):
        #开红灯
        GPIO.output(self.LED_R, GPIO.HIGH)
        GPIO.output(self.LED_G, GPIO.LOW)
        GPIO.output(self.LED_B, GPIO.LOW)
        self.back(20, 20)
        time.sleep(0.08)
        self.brake()
        
        #舵机旋转到0度，即右侧，测距
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 0)
        time.sleep(0.8)
        rightdistance = self.Distance_test()
    
        #舵机旋转到180度，即左侧，测距
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 180)
        time.sleep(0.8)
        leftdistance = self.Distance_test()

        #舵机旋转到90度，即前方，测距
        self.servo_appointed_detection(self.pwm_ultrasonic_servo, 90)
        time.sleep(0.8)
        frontdistance = self.Distance_test()
    
        if leftdistance < 30 and rightdistance < 30 and frontdistance < 30:
            #亮品红色，掉头
            GPIO.output(self.LED_R, GPIO.HIGH)
            GPIO.output(self.LED_G, GPIO.LOW)
            GPIO.output(self.LED_B, GPIO.HIGH)
            self.spin_right(85, 85)
            time.sleep(0.58)
        elif leftdistance >= rightdistance:
            #亮蓝色
            GPIO.output(self.LED_R, GPIO.LOW)
            GPIO.output(self.LED_G, GPIO.LOW)
            GPIO.output(self.LED_B, GPIO.HIGH)
            self.spin_left(85, 85)
            self.time.sleep(0.28)
        elif leftdistance <= rightdistance:
            #亮品红色，向右转
            GPIO.output(self.LED_R, GPIO.HIGH)
            GPIO.output(self.LED_G, GPIO.LOW)
            GPIO.output(self.LED_B, GPIO.HIGH)
            self.spin_right(85, 85)
            time.sleep(0.28)

