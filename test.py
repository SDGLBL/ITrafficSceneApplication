from detection import LpnDetector,Yolov3Detector,draw_label,get_random_bbox_colors
from PIL import Image
import numpy as np
import torch
from matplotlib import pyplot as plt
import time

# RTX2060速度0.68s处理30帧
if __name__ == "__main__":
    x = Yolov3Detector(batch_size=1,device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
    img = Image.open('./test.jpg').convert('RGB')
    img = np.array(img)
    imgs = []
    for _ in range(1):
        imgs.append(img)
    st = time.time()
    y = x(imgs,img.shape)
    et = time.time()
    print(et-st)
    bbox_colors = get_random_bbox_colors()
    img = draw_label(y[0],np.array(img),bbox_colors=bbox_colors)
    plt.imsave('./output.jpg',img)
    plt.show()