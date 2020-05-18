from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class saveImgInfo(BaseBackboneComponent):
    def __init__(self):
        super().__init__()

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs_info = kwargs['imgs_info']
        for img_info in imgs_info:
            print(img_info)
        return kwargs


