import argparse
import numpy as np
from time import time
from hyperlpr import HyperLPR_plate_recognition
import cv2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',type=str,help='the test images dir')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    img_path = args.i
    img = cv2.imread(img_path)
    st = time()
    result = HyperLPR_plate_recognition(img)
    et = time()
    print('识别车牌结果为:{0},耗时为{1}'.format(result,et-st))
