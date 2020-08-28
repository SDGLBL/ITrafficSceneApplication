from time import time

from utils.logger import get_logger
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class ProcessCollectorComponent(BaseBackboneComponent):
    def __init__(self, isPrint=False, figureStep=64):
        if figureStep % 2 != 0:
            raise AttributeError('figureStep必须为2的倍数')
        super().__init__()
        self.isPrint = isPrint
        self.currentStep = 0
        self.figureStep = figureStep
        self.logger = get_logger()
        self.startTime = None
        self.endTime = None

    def process(self, **kwargs):
        if self.startTime is None:
            self.startTime = time()
            
        self.currentStep += len(kwargs['imgs'])
        if self.currentStep == self.figureStep:
            info = kwargs['imgs_info'][-1]
            self.currentStep = 0
            if self.isPrint:
                self.logger.info('current process is {:3f}'.format(info['index']/info['video_len']))
        super().process(**kwargs)
        return None
