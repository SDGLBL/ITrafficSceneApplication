from components.registry import BACKBONE_C
import cv2
from cv2 import VideoWriter_fourcc
from components.backbones.base import BaseBackboneComponent
from utils import draw_label,get_random_bbox_colors


@BACKBONE_C.register_module
class WriteVideoBackboneComponent(BaseBackboneComponent):
    def __init__(self,resolution,fps,fourcc='mp4v',write_path='./save.mp4'):
        self.vwriter = cv2.VideoWriter(
            write_path,
            VideoWriter_fourcc(*fourcc),
            fps,
            resolution
        )
        self.colors = get_random_bbox_colors()
        super().__init__()

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs = kwargs['imgs']
        detections = kwargs['detections']
        for img,bboxs in zip(imgs,detections):
            img = draw_label(bboxs,img,self.colors)
            self.vwriter.write(img)


