import cv2
import os
import torch
import argparse
from matplotlib import pyplot as plt
from tqdm import tqdm
from components.backbones import DrawBoundingBoxComponent
from components.detector import Yolov3Detector,Yolov4Detector
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-td',type=str,default='./test_imgs',help='the test images dir')
    parser.add_argument('-od',type=str,default='./test_out',help='the out images dir')
    return parser.parse_args()


if __name__ == '__main__':
    """这只是一个演示脚本
       演示了从项目根目录读取test.mp4文件并写入到save.mp4文件
    """
    args = parse_args()
    detector = Yolov4Detector(
        device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'), batch_size=1, 
        img_size=608)
    if not os.path.exists(args.td):
        raise AttributeError('input path not exist')
    if not os.path.exists(args.od):
        os.mkdir(args.od)
    dlc = DrawBoundingBoxComponent()
    imgs_dir = args.td
    save_dir = args.od
    imgs_name = os.listdir(imgs_dir)
    for name in tqdm(imgs_name):
        img_path = os.path.join(imgs_dir,name)
        img = cv2.imread(img_path)
        imgs = [img]
        imgs_info = [{'shape':img.shape,'pass_count':0}]
        detections = detector(imgs=imgs,imgs_info=imgs_info)
        kwargs = dlc.process(imgs=imgs,imgs_info=imgs_info)
        output = kwargs['imgs'][0]
        save_name = name.split('.')[0]+'_result.jpg'
        save_path = os.path.join(save_dir,save_name)
        print(save_path)
        cv2.imwrite(save_path,output)
