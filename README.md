# travel-robot
This is a robot built on top of 4wd car which having RaspberryPi 4B chip and Camera.
The car will patrol around the room and identify any lost mobile phone on the ground and move towards it.
The tensor flow model is trained using EfficientDet, which is able to provide real time object recognition.

## Sample Command
```
python3 detect.py --model="/home/pi/robot/model/phone-1.tflite" --frameWidth=320 --frameHeight=240 --detectThreshold=0.5 --cameraYAngle=65
```
