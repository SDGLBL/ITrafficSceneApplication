#!/bin/bash
# Download common models

python -c "
import matplotlib
matplotlib.use('Agg')
from components.detector.yolov5.utilsv5.google_utils import *;
attempt_download('components/detector/yolov5/weights/yolov5s.pt');
attempt_download('components/detector/yolov5/weights/yolov5m.pt');
attempt_download('components/detector/yolov5/weights/yolov5l.pt');
attempt_download('components/detector/yolov5/weights/yolov5x.pt')
"
