import numpy as np

from components.backbones.base import BaseBackboneComponent
from components.backbones.registry import BACKBONE_COMPONENT
from utils.utils import bbox2center, identify_number_plate, point_distance,time2format_time,format_time2time


@BACKBONE_COMPONENT.register_module
class ParkingMonitoringComponent(BaseBackboneComponent):
    def __init__(self, monitoring_area: np.ndarray, allow_stop_time=180, check_step=30, is_process=False):

        """
        违章停车监控类
        Args:
            monitoring_area: 监控区域蒙版，在此区域内禁止超过allow_stop_time的目标都会被认为是违规停车目标
            allow_stop_time: 允许最长停车多久，单位为s（根据交通法规为3分钟)
            is_process: 是否开启该组件
        """
        super().__init__()
        self.monitoring_area = monitoring_area
        self.allow_stop_time = allow_stop_time
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
        if self.curent_step >= self.check_step:
            self.curent_step = 0
            # 每次只取一张进行处理
            img, img_info = imgs[0], imgs_info[0]
            # 如果达到一定的时间间隔检查一遍维护的列表
            if self.curent_step % (self.check_step * 10) == 0:
                for obj_id, obj in self.objs.items():
                    # 如果一个目标失去跟踪20s即将他删除
                    if format_time2time(img_info['time']) - obj['end_time'] > 20:
                        del self.objs[obj_id]
                        index = self.no_record_id.index(obj['id'])
                        del self.no_record_id[index]

            if img.shape[:2] != self.monitoring_area.shape[:2]:
                raise AttributeError('违规停车监测组件的监测区域遮罩矩阵大小必须与图像大小匹配')

            # 循环添加当前帧数里面停止在目标到跟踪dict
            for obj in img_info['objects']:
                if obj['cls_pred'] not in ['car','truck','bus']:
                    continue
                # 如果已经被记录为违章停车则不再记录
                obj_id = obj['id']
                if obj_id in self.no_record_id:
                    continue
                x_c, y_c = bbox2center(obj['bbox'])
                # 如果该目标的中心位于不允许停车区域,将其添加进入跟踪检查字典
                if self.monitoring_area[int(y_c), int(x_c)] == 0:
                    number_plate = identify_number_plate(img, obj['bbox'])
                    # 如果是第一次监测到
                    if obj_id not in self.objs.keys():
                        # print('当前时间为{}'.format(img_info['index'] // 30))
                        # print('id 为 {} 的目标进入禁止停车位置,车牌号为 {}'.format(obj['id'], number_plate))
                        self.objs[obj_id] = {
                            'point': (x_c, y_c),
                            'start_time': format_time2time(img_info['time']),
                            'end_time': None,
                            'imgs': [img],
                            'number_plate': number_plate
                        }
                    # 如果目标早已被监测，刷新其状态
                    else:
                        start_time = self.objs[obj_id]['start_time']
                        end_time = format_time2time(img_info['time'])
                        point = bbox2center(obj['bbox'])
                        self.objs[obj_id]['end_time'] = end_time
                        # print('{}目标早已被监测，刷新其状态'.format(obj_id))
                        # print('当前时间为{}'.format(img_info['index'] // 30))
                        # 如果超过允许停车的时间限度且没有移动
                        # print('{}目标停止时间为{}'.format(obj_id,end_time - start_time))
                        if end_time - start_time >= self.allow_stop_time and point_distance(point, self.objs[obj_id][
                            'point']) < 20:
                            # print('{} 超过允许停止时间限度，且没有移动，进行记录'.format(obj_id))
                            # 记录最后一张证据图
                            # 如果是完全不能停车的地方只需要记录一张违规截图
                            if self.allow_stop_time != 0:
                                self.objs[obj_id]['imgs'].append(img)
                            # 如果上次车牌号没检测出来继续检测识别
                            if self.objs[obj_id]['number_plate'] is None:
                                self.objs[obj_id]['number_plate'] = identify_number_plate(img, obj['bbox'])
                            # 在img_info中添加停车违规记录
                            img_info['analysis'].append({
                                'info_type': 'illegal_parking',
                                'id': obj_id,
                                'start_time': time2format_time(start_time),
                                'end_time': time2format_time(end_time),
                                'passage_type': 'None',  # 因为是违法停车，所以没有通行类型
                                'obj_type': obj['cls_pred'],
                                'number_plate': self.objs[obj_id]['number_plate'],
                                'imgs': self.objs[obj_id]['imgs']
                            })
                            self.no_record_id.append(obj_id)
                            del self.objs[obj_id]
                        # 如果没有移动且停车时间还未达到违规范围，刷新其end_time
                        elif point_distance(point, self.objs[obj_id]['point']) < 20:
                            # print('{}没有移动但停车时间还未达到违规范围'.format(obj_id))
                            self.objs[obj_id]['end_time'] = format_time2time(img_info['time'])
                            self.objs[obj_id]['point'] = bbox2center(obj['bbox'])
                            # 如果上次车牌号没检测出来继续检测识别
                            if self.objs[obj_id]['number_plate'] is None:
                                self.objs[obj_id]['number_plate'] = identify_number_plate(img, obj['bbox'])
                        # 如果移动了，我们认为改目标不算违章停车那就更新它的start_time
                        elif point_distance(point, self.objs[obj_id]['point']) > 100:
                            # print('{}移动了我们认为改目标不算违章停车那就更新它的start_time'.format(obj_id))
                            self.objs[obj_id]['start_time'] = format_time2time(img_info['time'])
                            # 刷新违规截图
                            self.objs[obj_id]['imgs'][0] = img
                            self.objs[obj_id]['point'] = bbox2center(obj['bbox'])
                        else:
                            # print('{}没有移动但停车时间还未达到违规范围'.format(obj_id))
                            self.objs[obj_id]['end_time'] = format_time2time(img_info['time'])
                            self.objs[obj_id]['point'] = bbox2center(obj['bbox'])

        else:
            self.curent_step += len(imgs_info)
        return kwargs
