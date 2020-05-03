# Intelligent traffic scene application

### Requirements

- Windows or Linux
- CUDA == 10.1
- cuDNN >= 7.4 for CUDA 10.1
- python3.7

### How to setup

#### Linux

```bash
bash setup.sh
```

#### Windows(cmd or powershell)

```
start setup.bat
```

### PretrainedWeights

- [Download weights for vanilla YOLOv3](https://pjreddie.com/media/files/yolov3.weights)
- [Download weights for tiny YOLOv3](https://pjreddie.com/media/files/yolov3-tiny.weights)
- [Download weights for backbones network](https://pjreddie.com/media/files/darknet53.conv.74)

Then place them in components/detector/yolov3/weights

### References

- https://github.com/eriklindernoren/PyTorch-YOLOv3
- https://github.com/zeusees/HyperLPR