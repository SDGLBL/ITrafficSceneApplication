import cv2
from cv2 import VideoWriter_fourcc
from utils import draw_label,get_random_bbox_colors
from components.backbones.registry import BACKBONE_COMPONENT
from components.backbones.base import BaseBackboneComponent

@BACKBONE_COMPONENT.register_module
class WriteVideoBackboneComponent(BaseBackboneComponent):
    def __init__(self,resolution,fps,fourcc='avc1',write_path='./save.mp4'):
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
            if bboxs is not None:
                print(img.shape)
                img = draw_label(bboxs, img, self.colors)
                self.vwriter.write(img)
            elif bboxs is None:
                # 如果没有探测到任何目标
                self.vwriter.write(img)