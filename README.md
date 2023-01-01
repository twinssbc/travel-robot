# travel-robot
<img width="201" alt="robot" src="https://user-images.githubusercontent.com/3329841/210164823-9c9eddec-93b8-45d1-a81e-66b9e20a6ceb.png">
This is a robot built on top of 4wd car which having RaspberryPi 4B chip and Camera.    
The car will patrol around the room and recognize any lost mobile phone on the ground and move towards it.    
The implementation is based on Python3 and TFLite (TensorFlow Lite) Object Detection API.    
The tensor flow model is trained using EfficientDet, which is able to achieve real time object recognition.  

## Demo Video
https://user-images.githubusercontent.com/3329841/210165747-e993c6b6-f162-430e-8c9d-0b43288c11c8.mp4

## Flow Chart
<img width="369" alt="flow chat" src="https://user-images.githubusercontent.com/3329841/210164833-0aac9e7a-d847-46c4-bdd2-ad1668332d8c.png">

## Sample Command
```
python3 detect.py --model="/home/pi/robot/model/phone-1.tflite" --frameWidth=320 --frameHeight=240 --detectThreshold=0.51 --cameraYAngle=62 --targetSizeThreshold=20
```
## Reference
https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/2.2.0/
https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md





