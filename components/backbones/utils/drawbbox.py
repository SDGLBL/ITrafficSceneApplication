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
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            # 首先检查是否探测到了bbox
            if 'objects' not in img_info.keys():
                # 说明没有经过探测器所以没用Objects信息
                continue
            bboxs = [obj['bbox'] for obj in img_info['objects']]
            obj_confs = [obj['obj_conf'] for obj in img_info['objects']]
            cls_confs = [obj['cls_conf'] for obj in img_info['objects']]
            cls_preds = [obj['cls_pred'] for obj in img_info['objects']]
            ids = [obj['id'] if 'id' in obj.keys() else 'None' for obj in img_info['objects']]

            draw_label(bboxs, obj_confs, cls_confs, cls_preds, ids, img, self.colors)
        return kwargs


