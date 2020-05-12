from ..registry import BACKBONE_COMPONENT
from ..base import BaseBackboneComponent

@BACKBONE_COMPONENT.register_module
class TrafficFlowCountingComponent(BaseBackboneComponent):
    def __init__(self):
        super().__init__()

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs_info = kwargs['imgs_info']
        return kwargs