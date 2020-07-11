import numpy as np

from components.backbones.base import BaseBackboneComponent
from components.backbones.registry import BACKBONE_COMPONENT
from utils.utils import bbox2center, point_distance,is_bbox_in_img,format_time2time,time2format_time,get_current_time

@BACKBONE_COMPONENT.register_module
class LaneMonitoringComponent(BaseBackboneComponent):
    def __init__(self,check_step=30, is_process = False):
        super().__init__()
        self.check_step = check_step
        self.is_process = is_process
    
    
    

    