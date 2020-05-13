from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class infoPort(BaseBackboneComponent):
    def __init__(self):
        tPaths = {}      # 路径缓存池
        environmentArg = {
            'HighGradePaths': [],    # 优质路径收集
            'HighGradeSpeed': []    # 优质速度矢量收集
        }
        speedTh = 10        # 速度阈值，超过该速度才会被保存
        pathLTh = 500       # 路径长度阈值，超过该长度才会被保存

    def img_info2Path(img_info):
        pass


    def process(self, **kwargs):
        imgs_info = kwargs['imgs_info']
        print(imgs_info[0])
        return kwargs

