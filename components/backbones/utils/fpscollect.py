from time import time

from utils.logger import get_logger
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class FpsCollectorComponent(BaseBackboneComponent):
    def __init__(self, isPrint=False, figureStep=64):
        if figureStep % 2 != 0:
            raise AttributeError('figureStep必须为2的倍数')
        super().__init__()
        self.isPrint = isPrint
        self.currentStep = 0
        self.figureStep = figureStep
        self.logger = get_logger(filename='logs/fpsCollect.log')
        self.startTime = None
        self.endTime = None

    def process(self, **kwargs):
        if self.startTime is None:
            self.startTime = time()
        self.currentStep += len(kwargs['imgs'])
        if self.currentStep == self.figureStep:
            self.endTime = time()
            fps = int(self.figureStep / (self.endTime - self.startTime))
            self.currentStep = 0
            self.startTime = None
            if self.isPrint:
                self.logger.info('current fps is {0}'.format(fps))
        super().process(**kwargs)
        return kwargs
