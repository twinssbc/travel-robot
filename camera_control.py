import RPi.GPIO as GPIO
import time
import cv2

class CameraControl:
    #云台舵机引脚定义
    Camera_ServoPin = 11  #S2
    Camera_ServoPinB = 9  #S3
    cap:any

    def init(self):
        GPIO.setup(self.Camera_ServoPin, GPIO.OUT)
        GPIO.setup(self.Camera_ServoPinB, GPIO.OUT)

        time.sleep(2)
        self.servo_control(90, 90)

        # Start capturing video input from the camera
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


    #定义一个脉冲函数，用来模拟方式产生pwm值
    #时基脉冲为20ms，该脉冲高电平部分在0.5-2.5ms控制0-180度
    def servo_pulse(self, servo, angle):
        pulsewidth = (angle * 11) + 500
        GPIO.output(servo, GPIO.HIGH)
        time.sleep(pulsewidth/1000000.0)
        GPIO.output(servo, GPIO.LOW)
        time.sleep(20.0/1000-pulsewidth/1000000.0)
        
    #控制云台，根据舵机脉冲控制范围为500-2500usec内：
    def servo_control(self, angle_1, angle_2):
        # if angle_1 < 500:
        #     angle_1 = 500
        # elif angle_1 > 2500:
        #     angle_1 = 2500
            
        # if angle_2 < 500:
        #     angle_2 = 500
        # elif angle_2 > 2500:
        #     angle_2 = 2500
        self.servo_pulse(self.Camera_ServoPin, angle_1)
        self.servo_pulse(self.Camera_ServoPinB, angle_2)

    def read_image(self):
        if self.cap.isOpened():
            return self.cap.read()
        else:
            return False, None