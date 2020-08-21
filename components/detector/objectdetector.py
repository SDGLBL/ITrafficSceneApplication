from time import time

import cv2
import numpy as np
import torch
import torchvision.transforms.functional as F
import os
from .base import BaseDetector
from .registry import DETECTOR
from .yolov3 import get_yolov3, pad_to_square, non_max_suppression, rescale_boxes
from .yolov4 import get_yolov4, get_region_boxes1, nms


@DETECTOR.register_module
class Yolov3Detector(BaseDetector):

    def __init__(self,
                 device,
                 conf_thres=0.8,
                 nms_thres=0.4,
                 img_size=416,
                 batch_size=1):
        """Yolov3目标探测网络
        Args:
            device (torch.device): 模型运行硬件 cuda or cpu
            conf_thres (float, optional): 目标置信度阈值. Defaults to 0.8.
            nms_thres (float, optional): 非极大值抑制阈值. Defaults to 0.4.
            img_size (int, optional): 网络输入大小. Defaults to 416.
            batch_size (int, optional): 批处理大小. Defaults to 1.
        """                          
        # 神经网络输入图像大小
        self.img_size = img_size
        # 置信度阈值
        self.conf_thres = conf_thres
        # 非极大值抑制阈值
        self.nms_thres = nms_thres
        #self._instanceLock =
        super(Yolov3Detector, self).__init__(
            model=get_yolov3(
                img_size=img_size,
            ),
            device=device,
            batch_size=batch_size)


    def preprocessing(self, imgs):
        """
        将输入的图像列表处理为batch
        Args:
            imgs (list[PIL.Image]) or list[np.ndarray] : 长度应该与batch_size匹配

        Returns:
            imgs_batch (torch.Tensor) : torch.Tensor shape like [N,C,H,W]
        """
        imgs = super().preprocessing(imgs)
        imgs = [self.__yolov3_img_pre(img) for img in imgs]
        imgs = [torch.unsqueeze(img,0) for img in imgs]
        imgs_batch = torch.cat(imgs,0).to(self.device)
        return imgs_batch


    def __yolov3_img_pre(self,img):
        """
        将图像处理为网络可以接受的大小
        Args:
            img (): PIL.Image or np.ndarray

        Returns:
            torch.Tensor
        """
        # Resize
        img_max_len = max(img.shape[:2])
        img_min_len = min(img.shape[:2])
        scale_num = img_max_len / self.img_size
        if img.shape[0] == img_max_len:
            target_size = (int(img_min_len/scale_num),self.img_size)
            img = cv2.resize(img,target_size)
        else:
            target_size = (self.img_size,int(img_min_len/scale_num))
            img = cv2.resize(img,target_size)
        img = F.to_tensor(img)
        # Pad to square resolution
        img, _ = pad_to_square(img, 0)
        return img


    def afterprocessing(self, detections: torch.Tensor,imgs_info: list):
        """
        非极大值抑制和rescale
        Args:
            detections: 神经网络的输出
            imgs_info:图像信息list

        Returns:imgs_info (list[dict]):图像信息list,其中每个img_info添加了obejcts

        """
        # NMS
        detections = non_max_suppression(detections,self.conf_thres,self.nms_thres)
        for index,detections_for_one in enumerate(detections):
            imgs_info[index]['objects'] = []
            if detections_for_one is None:
                # 没有探测到任何东西直接跳过
                continue
            shape = imgs_info[index]['shape']
            detections_for_one = rescale_boxes(detections_for_one, self.img_size, shape[:2])
            for x1, y1, x2, y2, obj_conf, cls_conf, cls_pred in detections_for_one:
                one_object_info = {
                    'bbox': [x1.item(), y1.item(), x2.item(), y2.item()],
                    'obj_conf': obj_conf.item(),
                    'cls_conf': cls_conf.item(),
                    'cls_pred': self.classes[int(cls_pred.item())]
                }
                imgs_info[index]['objects'].append(one_object_info)
        return imgs_info

    def __call__(self, **kwargs):
        """
        YoLov3前传函数
        Args:
            imgs: 图像list or 图像 np.ndarray len(imgs)一个与batch_size匹配 
            imgs_info: 图像信息list，其中需要包含如下信息
            imgs_info[index] = {
                'time':time,
                'index':index,
                'shape':shape,
            }

        Returns:
            imgs_info: 图像信息list,其中每个img_info添加了obejcts

        """
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        t0 = time()
        imgs_batch = self.preprocessing(imgs)
        t1 = time()
        with torch.no_grad():
            detections = self.model(imgs_batch)
        t2 = time()
        imgs_info = self.afterprocessing(detections, imgs_info)
        t3 = time()
        if False:
            print('|-----------------------------------|')
            print('preprocessing use {0}'.format(t1-t0))
            print('inference use {0}'.format(t2-t1))
            print('afterprocessing use {0}'.format(t3-t2))
            print('|-----------------------------------|')
        return {'imgs': imgs, 'imgs_info': imgs_info}


@DETECTOR.register_module
class Yolov4Detector(BaseDetector):

    def __init__(
        self, device,
        conf_thres=0.8,
        nms_thres=0.4,
        img_size=416,
        batch_size=1,
        cfgs='./components/detector/yolov4/cfg/yolov4.cfg',
        weightp='./components/detector/yolov4/weight/yolov4.weights'):
        """Yolov4目标探测网络
        Args:
            device (torch.device): 模型运行硬件 cuda or cpu
            conf_thres (float, optional): 目标置信度阈值. Defaults to 0.8.
            nms_thres (float, optional): 非极大值抑制阈值. Defaults to 0.4.
            img_size (int, optional): 网络输入大小. Defaults to 416.
            batch_size (int, optional): 批处理大小. Defaults to 1.
        """     
        # 神经网络输入图像大小
        self.img_size = img_size
        # 置信度阈值
        self.conf_thres = conf_thres
        # 非极大值抑制阈值
        self.nms_thres = nms_thres
        model = get_yolov4(cfgs,weightp,img_size)
        super().__init__(model, device, batch_size)

    def preprocessing(self, imgs: list):
        """
        将输入的图像列表处理为batch
        Args:
            imgs (list[PIL.Image]) or list[np.ndarray] : 长度应该与batch_size匹配

        Returns:
            imgs_batch (torch.Tensor) : torch.Tensor shape like [N,C,H,W]
        """
        imgs = super().preprocessing(imgs)
        imgs = [self.__yolov4_img_pre(img) for img in imgs]
        imgs = [torch.unsqueeze(img, 0) for img in imgs]
        imgs_batch = torch.cat(imgs, 0).to(self.device)
        return imgs_batch

    def __yolov4_img_pre(self, img):
        """
            将图像处理为网络可以接受的大小
            Args:
                img (): PIL.Image or np.ndarray

            Returns:
                torch.Tensor
        """
        # Resize
        img_max_len = max(img.shape[:2])
        img_min_len = min(img.shape[:2])
        scale_num = img_max_len / self.img_size
        if img.shape[0] == img_max_len:
            target_size = (int(img_min_len/scale_num),self.img_size)
            img = cv2.resize(img,target_size)
        else:
            target_size = (self.img_size,int(img_min_len/scale_num))
            img = cv2.resize(img,target_size)
        img = F.to_tensor(img)
        # Pad to square resolution
        img, _ = pad_to_square(img, 0)
        return img

    def afterprocessing(self, detections: list, imgs_info:list):
        """
        非极大值抑制和rescale
        Args:
            detections: 神经网络的输出
            imgs_info:图像信息list

        Returns:imgs_info (list[dict]):图像信息list,其中每个img_info添加了obejcts

        """
        anchors = [12, 16, 19, 36, 40, 28, 36, 75, 76, 55, 72, 146, 142, 110, 192, 243, 459, 401]
        num_anchors = 9
        anchor_masks = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        strides = [8, 16, 32]
        anchor_step = len(anchors) // num_anchors
        detections = [detection.cpu().numpy() for detection in detections]
        bboxs_for_imgs = []
        for i in range(1,3):
            masked_anchors = []
            for m in anchor_masks[i]:
                masked_anchors += anchors[m * anchor_step:(m + 1) * anchor_step]
            masked_anchors = [anchor / strides[i] for anchor in masked_anchors]
            bboxs_for_imgs.append(get_region_boxes1(detections[i], 0.6, 80, masked_anchors, len(anchor_masks[i])))

        bboxs_for_imgs = [
            bboxs_for_imgs[0][index] + bboxs_for_imgs[1][index]
            for index in range(self.batch_size)]
        # bboxs_for_imgs = [
        #     bboxs_for_imgs[0][index] + bboxs_for_imgs[1][index] + bboxs_for_imgs[2][index]
        #     for index in range(self.batch_size)]
        # 分别对每一张图片的结果进行nms
        detections = [nms(bboxs, self.nms_thres) for bboxs in bboxs_for_imgs]
        detections = [np.array(bboxs) for bboxs in detections]
        # 非极大值抑制后可能出现没有任何目标被探测出
        for index, detections_for_one in enumerate(detections):
            imgs_info[index]['objects'] = []
            if detections_for_one is None:
                # 没有探测到任何东西直接跳过
                continue
            img_shape = imgs_info[index]['shape']  # 获取图像shape
            max_shape = max(img_shape[:-1])
            min_shape = min(img_shape[:-1])
            pad_size = (max_shape - min_shape) // 2
            width = img_shape[1]
            height = img_shape[0]
            for i in range(len(detections_for_one)):
                bbox = detections_for_one[i]
                x1 = int((bbox[0] - bbox[2] / 2.0) * max_shape)
                y1 = int((bbox[1] - bbox[3] / 2.0) * max_shape)
                x2 = int((bbox[0] + bbox[2] / 2.0) * max_shape)
                y2 = int((bbox[1] + bbox[3] / 2.0) * max_shape)
                # 如果是按照长度作为pad后的正方图像大小,则需要平移y轴一个padsize
                if width == max_shape:
                    y1 -= pad_size
                    y2 -= pad_size
                # if height == max_shape
                else:
                    x1 -= pad_size
                    x2 -= pad_size
                obj_conf = detections_for_one[i][4]
                cls_conf = detections_for_one[i][5]
                cls_pred = detections_for_one[i][6]
                detections_for_one[i] = [x1, y1, x2, y2, obj_conf, cls_conf, cls_pred]
            for x1, y1, x2, y2, obj_conf, cls_conf, cls_pred in detections_for_one:
                one_object_info = {
                    'bbox': [x1, y1, x2, y2],
                    'obj_conf': obj_conf,
                    'cls_conf': cls_conf,
                    'cls_pred': self.classes[int(cls_pred.item())]
                }
                imgs_info[index]['objects'].append(one_object_info)
        return imgs_info

    def __call__(self, **kwargs):
        """
        YoLov4前传函数
        Args:
            imgs: 图像list or 图像 np.ndarray len(imgs)一个与batch_size匹配 
            imgs_info: 图像信息list，其中需要包含如下信息
            imgs_info[index] = {
                'time':time,
                'index':index, 
                'shape':shape, (H,W,C)
            }

        Returns:
            imgs_info: 图像信息list,其中每个img_info添加了obejcts
        """
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        imgs_batch = self.preprocessing(imgs)
        t1 = time()
        with torch.no_grad():
            detections = self.model(imgs_batch)
            # torch.cuda.synchronize()
        t2 = time()
        imgs_info = self.afterprocessing(detections, imgs_info)
        t3 = time()
        if False:
            print('|-----------------------------------|')
            print('preprocessing use {0}'.format(t1-t0))
            print('inference use {0}'.format(t2-t1))
            print('afterprocessing use {0}'.format(t3-t2))
            print('|-----------------------------------|')
        return {'imgs': imgs, 'imgs_info': imgs_info}


from models.experimental import attempt_load
from components.detector.yolov5.utilsv5.datasets import letterbox
from components.detector.yolov5.utilsv5.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords,
    xyxy2xywh, plot_one_box, strip_optimizer, set_logging)
from components.detector.yolov5.utilsv5.torch_utils import select_device, load_classifier
import random

@DETECTOR.register_module
class Yolov5Detector(BaseDetector):
    def __init__(self,
                 device='0',
                 conf_thres=0.4,
                 nms_thres=0.4,
                 img_size=640,
                 batch_size=1,
                 weights='./components/detector/yolov5/weights/yolov5m.pt',
                 half = False):
        self.device = select_device(device)
        self.conf_thres = conf_thres
        import os
        x = os.getcwd()
        self.model = attempt_load(weights, map_location=self.device)
        self.img_size = check_img_size(img_size, s=self.model.stride.max())
        if half:
            self.model.half()  # to FP16
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]
        self.half = half
        self.iou_thres = 0.6
        super().__init__(self.model, self.device, batch_size)

    def preprocessing(self, imgs):
        imgs = [letterbox(img,new_shape=self.img_size)[0] for img in imgs]
        imgs = [img[:, :, ::-1].transpose(2, 0, 1) for img in imgs]
        imgs = [np.ascontiguousarray(img) for img in imgs]
        imgs = [torch.from_numpy(img) for img in imgs]
        if self.half:
            imgs = [img.half() for img in imgs]
        imgs = [img / 255.0 for img in imgs]
        imgs = [img.unsqueeze(0) for img in imgs]
        imgs = torch.cat(imgs,0).to(self.device)
        return imgs

    def afterprocessing(self, detections, imgs_batch, imgs_info):
        preds = non_max_suppression(detections, self.conf_thres, self.iou_thres)
        for i,det in enumerate(preds):
            if det is not None and len(det):
                det[:, :4] = scale_coords(imgs_batch.shape[2:], det[:, :4], imgs_info[i]['shape']).round()
                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s = '%g %ss, ' % (n, self.names[int(c)])  # add to string
                imgs_info[i]['objects'] = []
                # Write results
                for *xyxy, conf, cls in reversed(det):
                    x1, y1, x2, y2 = xyxy
                    x1, y1, x2, y2 = x1.cpu().item(),y1.cpu().item(), x2.cpu().item(), y2.cpu().item()
                    obj_conf = conf.cpu().item()
                    cls_conf = obj_conf
                    cls_pred = cls.cpu().item()
                    imgs_info[i]['objects'].append({
                        'bbox': [x1, y1, x2, y2],
                        'obj_conf': obj_conf,
                        'cls_conf': cls_conf,
                        'cls_pred': self.classes[int(cls_pred)]
                    })
        return imgs_info

    def __call__(self, **kwargs):
        """
        YoLov5前传函数
        Args:
            imgs: 图像list or 图像 np.ndarray len(imgs)一个与batch_size匹配 
            imgs_info: 图像信息list，其中需要包含如下信息
            imgs_info[index] = {
                'time':time,
                'index':index, 
                'shape':shape, (H,W,C)
            }

        Returns:
            imgs_info: 图像信息list,其中每个img_info添加了obejcts
        """
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        imgs_batch = self.preprocessing(imgs)
        with torch.no_grad():
            preds = self.model(imgs_batch, augment=False)[0]
        imgs_info = self.afterprocessing(preds,imgs_batch,imgs_info)
        return {'imgs': imgs, 'imgs_info': imgs_info}
