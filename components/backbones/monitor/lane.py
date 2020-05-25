import numpy as np

from components.backbones.base import BaseBackboneComponent
from components.backbones.registry import BACKBONE_COMPONENT
from utils.dao import fomate_time2time, time2fomate_time
from utils.utils import bbox2center, identify_number_plate, point_distance,is_bbox_in_img


@BACKBONE_COMPONENT.register_module
class LaneMonitoringComponent(BaseBackboneComponent):
    def __init__(self, monitoring_area: np.ndarray, no_allow_car={}, check_step=30):

        """
        违章占用车道监控类
        Args:
            monitoring_area: 监控区域蒙版
            no_allow_car: 某区域不允许停放的车辆
        Example:
            no_allow_car = {1:['car','truck']}
            则在monitoring_area中值为1的区域内不允许出现car和truck
        """
        super().__init__()
        self.monitoring_area = monitoring_area
        self.no_allow_car = no_allow_car
        self.check_step = check_step  # 检查间隔 每隔多少步进行检查 默认为30帧一秒一次
        self.curent_step = 0
        self.objs = {}
        self.no_record_id = []

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        if self.curent_step >= self.check_step:
            self.curent_step = 0
            # 每次只取一张进行处理
            img, img_info = imgs[0], imgs_info[0]
            # 如果达到一定的时间间隔检查一遍维护的列表
            if self.curent_step % (self.check_step * 10):
                for index, obj in self.objs:
                    # 如果一个目标失去跟踪20s即将他删除
                    if fomate_time2time(img_info['time']) - obj['end_time'] > 20:
                        del self.objs[index]
                        index = self.no_record_id.index(obj['id'])
                        del self.no_record_id[index]

            if img.shape[:2] != self.monitoring_area.shape[:2]:
                raise AttributeError('违法占用车道监测组件的监测区域遮罩矩阵大小必须与图像大小匹配')

            # 循环添加当前帧数里面停止在目标到跟踪dict
            for obj in img_info['objects']:
                # 如果已经被记录为违章停车则不再记录
                obj_id = obj['id']
                if obj_id in self.no_record_id:
                    continue
                # 如果目标还没有全部出现在视野中直接跳过
                if not is_bbox_in_img(img,obj['bbox']):
                    continue
                x_c, y_c = bbox2center(obj['bbox'])
                # 如果该目标的中心位于检测区域
                current_position_type = self.monitoring_area[int(y_c), int(x_c)]
                start_time = self.objs[obj_id]['start_time']
                end_time = fomate_time2time(img_info['time'])
                if current_position_type in self.no_allow_car.keys():
                    # 如果目标的类别不允许出现在这个区域内则进行记录
                    if obj['cls_pred'] in self.no_allow_car[current_position_type]:
                        img_info['analysis'].append({
                                'info_type': 'illegal_occupation',
                                'id': obj_id,
                                'start_time': time2fomate_time(start_time),
                                'end_time': time2fomate_time(end_time),
                                'passage_type': 'None',  # 因为是违法占用车道，所以没有通行类型
                                'obj_type': obj['cls_pred'],
                                'number_plate': self.objs[obj_id]['number_plate'],
                                'imgs': [img,img]
                            })
                        # 将该车辆记录为不再追踪车辆，因为其违法记录已经捕捉
                        self.no_record_id.append(obj_id)
        return kwargs
