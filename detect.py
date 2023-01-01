# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#####################
# Sample Command
# python3 detect.py --model="/home/pi/robot/model/phone-1.tflite" --frameWidth=320 --frameHeight=240 --detectThreshold=0.5 --cameraYAngle=65
#####################

"""Main script to run the object detection routine."""
import argparse
import sys
import time
import logging

from object_detector import ObjectDetector
from object_detector import ObjectDetectorOptions
from car_control import CarControl
from camera_control import CameraControl
from notification import Notification

def run(model: str, camera_id: int, width: int, height: int, num_threads: int, detect_threshold: float,
        speed: int, camera_x_angle: int, camera_y_angle: int, notification: bool, target_size_threshold: int) -> None:
    """Continuously run inference on images acquired from the camera.

    Args:
      model: Name of the TFLite object detection model.
      camera_id: The camera id to be passed to OpenCV.
      width: The width of the frame captured from the camera.
      height: The height of the frame captured from the camera.
      num_threads: The number of CPU threads to run the model.
      speed: car speed.
    """
    car = CarControl(speed)
    camera = CameraControl(camera_id, width, height,
                           camera_x_angle, camera_y_angle)

    car.init()
    camera.init()

    # Variables to calculate FPS
    counter, fps = 0, 0
    start_time = time.time()

    # Initialize the object detection model
    options = ObjectDetectorOptions(
        num_threads=num_threads,
        score_threshold=detect_threshold,
        max_results=3,
        enable_edgetpu=False)
    detector = ObjectDetector(model_path=model, options=options)

    center_x = width / 2
    center_y = height / 2
    x_axis_offset_threshold = width / 4
    y_axis_offset_threshold = height / 4

    detect_count = 0
    detect_total_score = 0
    detect_total_count = 3
    has_target = False
    max_size_ratio = 0
    no_target_count = 0
    no_target_total_count = 30

    enable_search = True
    close_enough_count = 0

    while True:
        success, image = camera.read_image()
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )

        # image = cv2.flip(image, 1)
        logging.debug("start detection")
        # Run object detection estimation using the model.
        detections = detector.detect(image)
        logging.debug("detect result: %s", detections)

        if len(detections) > 0:
            detect_count += 1
            detect_total_score += detections[0].categories[0].score
        else:
            detect_count = 0
            detect_total_score = 0
            has_target = False

        # Only detect target after successive {detect_total_count} times hit
        if detect_count >= detect_total_count:
            average_score = detect_total_score / detect_total_count
            if average_score > detect_threshold:
                has_target = True

        if has_target:
            enable_search = False
            # If camera angle is not front, spin the car to the camera angle, also reset the camera accordingly
            # Ultimately the car will face to the target, and camera is at front position
            camera_angle = camera.current_x_angle()
            if camera_angle < 85:
                logging.info("camera face right, turn right")
                car.spin_right(20, 20)
                time.sleep(0.05)
                car.brake()
                car.alert_find_target()
                camera.adjust_left()
                continue
            elif camera_angle > 95:
                logging.info("camera face left, turn left")
                car.spin_left(20, 20)
                time.sleep(0.05)
                car.brake()
                car.alert_find_target()
                camera.adjust_right()
                continue

            logging.info("detection result (score: %s): %s",
                         average_score, detections)
            bounding_box = detections[0].bounding_box
            result_center_x = (bounding_box.left + bounding_box.right) / 2
            result_center_y = (bounding_box.top + bounding_box.bottom) / 2
            logging.info("center (%s, %s), target (%s, %s)",
                         center_x, center_y, result_center_x, result_center_y)

            # If the target is below the screen, move the camera lower
            if result_center_y - center_y > y_axis_offset_threshold:
                camera.adjust_lower()

            # If the target size occupies certain ratio of the viewport, means we are closing to the target
            target_size = (bounding_box.right - bounding_box.left) * \
                (bounding_box.bottom - bounding_box.top)
            viewport_size = width * height
            target_size_ratio = target_size/viewport_size
            if target_size_ratio > max_size_ratio:
                max_size_ratio = target_size_ratio
            logging.info("target size ratio: %s, max ratio: %s",
                         target_size_ratio, max_size_ratio)
            if target_size/viewport_size * 100 > target_size_threshold:
                car.alert_close_to_target()
                logging.info("target close enough")
                if notification:
                    if close_enough_count > 3:
                        notification_agent = Notification()
                        notification_agent.send_wechat(image)
                        notification = False
                    else:
                        close_enough_count += 1
                continue
            if result_center_x - center_x > x_axis_offset_threshold:
                logging.info("target at right, spin right")
                car.spin_right(30, 30)
                time.sleep(0.08)
                car.brake()
                car.alert_find_target()
            elif center_x - result_center_x > x_axis_offset_threshold:
                logging.info("target at left: spin left")
                car.spin_left(30, 30)
                time.sleep(0.08)
                car.brake()
                car.alert_find_target()
            else:
                logging.info("target at the front of the car, move forward")
                car.run(30, 30)
                time.sleep(0.08)
                car.brake()
                car.alert_find_target()

            # reset detection
            detect_count = 0
            detect_total_score = 0
            has_target = False
        else:
            logging.info("no target found")
            no_target_count += 1
            car.alert_no_target()
            if enable_search:
                camera.search()
            else:
                if no_target_count >= no_target_total_count:
                    enable_search = True
                    no_target_count = 0
        # input_string = input("type anything to continue, q to quit")
        # if input_string == 'q':
        #     break

        # if car.face_obstacle():
        #     if findTarget:
        #         logging.info("find target, but can't proceed, stop")
        #     # else:
        #     #     car.find_way()
        # else:
        #     car.run()
    camera.release()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model',
        help='Path of the object detection model.',
        required=False,
        default='efficientdet_lite0.tflite')
    parser.add_argument(
        '--cameraId',
        help='Id of camera.',
        required=False,
        type=int,
        default=0)
    parser.add_argument(
        '--cameraXAngle',
        help='Init X angle of camera.',
        required=False,
        type=int,
        default=90)
    parser.add_argument(
        '--cameraYAngle',
        help='Init Y angle of camera.',
        required=False,
        type=int,
        default=65)
    parser.add_argument(
        '--frameWidth',
        help='Width of frame to capture from camera.',
        required=False,
        type=int,
        default=640)
    parser.add_argument(
        '--frameHeight',
        help='Height of frame to capture from camera.',
        required=False,
        type=int,
        default=480)
    parser.add_argument(
        '--numThreads',
        help='Number of CPU threads to run the model.',
        required=False,
        type=int,
        default=4)
    parser.add_argument(
        '--detectThreshold',
        help='Detect threshold.',
        required=False,
        type=float,
        default=0.5)
    parser.add_argument(
        '--speed',
        help='car speed',
        required=False,
        type=int,
        default=100)
    parser.add_argument(
        '--notification',
        help='notification',
        required=False,
        type=bool,
        default=False)
    parser.add_argument(
        '--targetSizeThreshold',
        help='target size threshold',
        required=False,
        type=int,
        default=20)
    args = parser.parse_args()

    run(args.model, int(args.cameraId), args.frameWidth, args.frameHeight,
        int(args.numThreads), float(args.detectThreshold), int(args.speed), int(args.cameraXAngle), int(args.cameraYAngle), args.notification, int(args.targetSizeThreshold))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    main()
