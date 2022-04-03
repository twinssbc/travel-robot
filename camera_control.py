import RPi.GPIO as GPIO
import time
import cv2
import logging


class CameraControl:
    # Camera Servo Pin
    Camera_ServoPin = 11  # S2
    Camera_ServoPinB = 9  # S3
    cap: any
    search_direction = 1

    def __init__(self, camera_id, width, height, camera_x_angle, camera_y_angle) -> None:
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.camera_x_angle = camera_x_angle
        self.camera_y_angle = camera_y_angle
        pass

    def init(self):
        logging.info("start initing camera control [width: %s, height: %s, camera X angle: %s, camera Y angle: %s]",
                     self.width, self.height, self.camera_x_angle, self.camera_y_angle)

        GPIO.setup(self.Camera_ServoPin, GPIO.OUT)
        GPIO.setup(self.Camera_ServoPinB, GPIO.OUT)

        time.sleep(2)

        count = 5
        while count > 0:
            self.servo_control(self.camera_x_angle, self.camera_y_angle)
            count -= 1

        # Start capturing video input from the camera
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        logging.info("complete initing camera control")

    def adjust_lower(self):
        if self.camera_y_angle > 58:
            self.camera_y_angle -= 3
            logging.info("adjust camera lower: %s", self.camera_y_angle)
            self.servo_pulse(self.Camera_ServoPinB, self.camera_y_angle)
    
    def search(self):
        if self.search_direction == 1:
            if  self.camera_x_angle < 150:
                self.camera_x_angle += 5
            else:
                self.search_direction = -1
        else:
            if self.camera_x_angle > 30:
                self.camera_x_angle -= 5
            else:
                self.search_direction = 1
        logging.info("search... direction: %s, angle: %s", self.search_direction, self.camera_x_angle)
        self.servo_pulse(self.Camera_ServoPin, self.camera_x_angle)

    def current_x_angle(self):
        return self.camera_x_angle

    def reset_x_angle(self):
        self.servo_pulse(self.Camera_ServoPin, 90)

    def adjust_left(self):
        if self.camera_x_angle < 170:
            self.camera_x_angle += 3
        logging.info("adjust camera left: %s", self.camera_x_angle)
        self.servo_pulse(self.Camera_ServoPin, self.camera_x_angle)

    def adjust_right(self):
        if self.camera_x_angle > 10:
            self.camera_x_angle -= 5
        logging.info("adjust camera right: %s", self.camera_x_angle)
        self.servo_pulse(self.Camera_ServoPin, self.camera_x_angle)

    # define a pulse function, generate pwm using simulation way
    # base pulse 20ms, maintain high level range within 0.5-2.5ms to control 0-180 angle
    def servo_pulse(self, servo, angle):
        pulsewidth = (angle * 11) + 500
        logging.debug("camera pulse: " + str(servo) +
                     ", angle: " + str(pulsewidth))
        GPIO.output(servo, GPIO.HIGH)
        time.sleep(pulsewidth/1000000.0)
        GPIO.output(servo, GPIO.LOW)
        time.sleep(20.0/1000-pulsewidth/1000000.0)

    def servo_control(self, angle_1, angle_2):
        self.servo_pulse(self.Camera_ServoPin, angle_1)
        self.servo_pulse(self.Camera_ServoPinB, angle_2)

    def read_image(self):
        if self.cap.isOpened():
            return self.cap.read()
        else:
            return False, None

    def release(self):
        if self.cap:
            self.cap.release()