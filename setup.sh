#!/bin/bash
pip3 install -r requirements.txt
cd .\components\detector\yolov3\weights
echo Download weights for vanilla YOLOv3
wget -c https://pjreddie.com/media/files/yolov3.weights
echo Download weights for tiny YOLOv3
wget -c https://pjreddie.com/media/files/yolov3-tiny.weights
echo Download weights for backbones network
wget -c https://pjreddie.com/media/files/darknet53.conv.74