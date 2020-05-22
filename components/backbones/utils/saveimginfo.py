import json

from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class SaveImgInfo(BaseBackboneComponent):
    """
    此类用于固化数据，如无必要请勿使用
    """

    def __init__(self, savePath='img_info.json'):
        super().__init__()
        self.savePath = savePath

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs_info = kwargs['imgs_info']
        for img_info in imgs_info:
            # print(img_info)
            with open(self.savePath, 'a+', encoding='utf-8') as f:
                line = json.dumps(img_info, ensure_ascii=False)
                f.write(line+'\n')
        return kwargs

