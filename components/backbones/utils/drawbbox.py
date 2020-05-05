from utils.utils import draw_label, get_random_bbox_colors
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class DrawBoundingBoxComponent(BaseBackboneComponent):
    def __init__(self):
        super().__init__()
        self.colors = get_random_bbox_colors()

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs = kwargs['imgs']
        detections = kwargs['detections']
        for img, bboxs in zip(imgs, detections):
            if bboxs is not None:
                # 探测到了bboxs才进行绘制
                draw_label(bboxs, img, self.colors)
        return kwargs


