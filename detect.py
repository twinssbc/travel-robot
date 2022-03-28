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
"""Main script to run the object detection routine."""
import argparse
import sys
import time
import cv2
import logging

from object_detector import ObjectDetector
from object_detector import ObjectDetectorOptions
from car_control import CarControl
from camera_control import CameraControl
# import utils


def run(model: str, camera_id: int, width: int, height: int, num_threads: int, detect_threshold: float,
        speed: int) -> None:
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
    camera = CameraControl()

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
        enable_edgetpu=enable_edgetpu)
    detector = ObjectDetector(model_path=model, options=options)

    while True:
        success, image  = camera.read_image()
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )

        image = cv2.flip(image, 1)
        logging.info("start detection")
        # Run object detection estimation using the model.
        detections = detector.detect(image)
        logging.info("detection result: ", detections)
        logging.info("complete detection")

        findTarget = False
        if len(detections) > 0:
            findTarget = True
            result = detections[0]
            car.adjustDirection()
        if car.meetObstacle():
            if findTarget:
                logging.info("find target, but can't proceed, stop")
            else:
                car.findWay()
        else:
            car.run()




    # Continuously capture images from the camera and run inference
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )

        counter += 1
        image = cv2.flip(image, 1)

        print(time.time(), "start detection")
        # Run object detection estimation using the model.
        detections = detector.detect(image)
        print("detection result: ", detections)
        print(time.time(), "complete detection")

        # Draw keypoints and edges on input image
        # image = utils.visualize(image, detections)

        # # Calculate the FPS
        # if counter % fps_avg_frame_count == 0:
        #   end_time = time.time()
        #   fps = fps_avg_frame_count / (end_time - start_time)
        #   start_time = time.time()

        # # Show the FPS
        # fps_text = 'FPS = {:.1f}'.format(fps)
        # text_location = (left_margin, row_size)
        # cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
        #             font_size, text_color, font_thickness)
        # Stop the program if the ESC key is pressed.
        # if cv2.waitKey(1) == 27:
        #   break
        # cv2.imshow('object_detector', image)

    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model',
        help='Path of the object detection model.',
        required=False,
        default='efficientdet_lite0.tflite')
    parser.add_argument(
        '--cameraId', help='Id of camera.', required=False, type=int, default=0)
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
    args = parser.parse_args()

    run(args.model, int(args.cameraId), args.frameWidth, args.frameHeight,
        int(args.numThreads), float(args.detectThreshold), int(args.speed))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s')
    main()
