import numpy as np

from components.backbones.base import BaseBackboneComponent
from components.backbones.registry import BACKBONE_COMPONENT
from utils.utils import bbox2center, identify_number_plate, point_distance,is_bbox_in_img,format_time2time,time2format_time,get_current_time,draw_illegal_label


@BACKBONE_COMPONENT.register_module
class LaneMonitoringComponent(BaseBackboneComponent):
    def __init__(self, monitoring_area: np.ndarray, no_allow_car={}, check_step=15, is_process = False):

        """
        违章占用车道监控类
        Args:
            monitoring_area: 监控区域蒙版
            no_allow_car: 某区域不允许停放的车辆
            is_process: 是否开启该组件
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
        self.is_process = is_process

    def process(self, **kwargs):
        super().process(**kwargs)
        if not self.is_process:
            return kwargs
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        self.curent_step += len(imgs)
        if self.curent_step >= self.check_step:
            self.curent_step = 0
            # 每次只取一张进行处理
            img, img_info = imgs[0], imgs_info[0]

            if img.shape[:2] != self.monitoring_area.shape[:2]:
                raise AttributeError('违法占用车道监测组件的监测区域遮罩矩阵大小必须与图像大小匹配')

            # 循环添加当前帧数里面停止在目标到跟踪dict
            for obj in img_info['objects']:
                if obj['cls_pred'] not in ['car','truck','bus']:
                    continue
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
                start_time = format_time2time(img_info['time'])
                end_time = format_time2time(img_info['time'])
                # if int(obj_id) == 23:
                #     print('23号目标被探测')
                #     print('x:{0}-y:{1}'.format(int(x_c),int(y_c)))
                #     print('current tyep is {}'.format(current_position_type))
                #     print(self.no_allow_car.keys())
                current_position_type = str(int(current_position_type))
                if current_position_type in self.no_allow_car.keys():
                    # 如果目标的类别不允许出现在这个区域内则进行记录
                    number_plate = identify_number_plate(img, obj['bbox'])
                    # 如果车牌没有被识别到则放弃这次拍照
                    if number_plate is None:
                        continue
                    if obj['cls_pred'] in self.no_allow_car[current_position_type]:
                        draw_img = draw_illegal_label(
                                    bbox=obj['bbox'],
                                    obj_conf=obj['obj_conf'],
                                    cls_pred=obj['cls_pred'],
                                    cls_conf=obj['cls_conf'],
                                    id=obj_id,
                                    img=img,
                                    number_plate = number_plate)
                        img_info['analysis'].append({
                                'info_type': 'illegal_occupation',
                                'id': obj_id,
                                'start_time': time2format_time(start_time),
                                'end_time': time2format_time(end_time),
                                'passage_type': 'None',  # 因为是违法占用车道，所以没有通行类型
                                'obj_type': obj['cls_pred'],
                                'number_plate': number_plate,
                                'imgs': [draw_img,draw_img]
                            })
                        # 将该车辆记录为不再追踪车辆，因为其违法记录已经捕捉
                        self.no_record_id.append(obj_id)
        return kwargs
