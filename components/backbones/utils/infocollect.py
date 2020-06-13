import os
import os.path as osp
from functools import reduce

import cv2

from utils.sqlitedao import get_connection, excute_sql, create_database
from utils.utils import format_time2time,time2format_time
from cfg import DataConfig
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class InformationCollectorComponent(BaseBackboneComponent):
    """
    收集信息，存往数据库
    """

    def __init__(
            self,
            process_type=['pass', 'illegal_parking']):
        """收集违规信息并存入数据库中

        Args:
            process_type (list, optional):支持处理的事件类型. Defaults to ['pass', 'illegal_parking'].
        """            
        super().__init__()
        create_database(clear_exist=True)
        self.connection = get_connection(DataConfig.DATABASE_PATH)
        self.process_type = process_type
        self.img_save_path = DataConfig.CRIMINAL_DIR
        if not osp.exists(self.img_save_path):
            os.mkdir(self.img_save_path)

    def process(self, **kwargs):
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img, img_info in zip(imgs, imgs_info):
            # 取出每一帧中的分析数据
            img_analysis_info = img_info['analysis']
            # 处理其中的每一个信息
            for info in img_analysis_info:
                info_type = info['info_type']
                if info_type not in self.process_type:
                    raise AttributeError('该组件不支持处理类型为{}的车辆通行数据'.format(info_type))
                # 如果为可以进行处理的数据则开始进行处理
                object_id = info['id']  # 目标id
                start_time = format_time2time(info['start_time'] ) # 被开始跟踪时间点
                end_time = format_time2time(info['end_time'])  # 结束跟踪时间点
                passage_type = info['passage_type']  # 通行类型  直行 左转 右行
                obj_type = info['obj_type']  # 目标类型
                number_plate = info['number_plate']  # 车牌号 车牌号
                start_time_id = time2format_time(start_time) + ' ' + str(object_id)
                # 处理通过信息
                if info_type == 'pass':
                    excute_sql(
                        self.connection,
                        'INSERT INTO traffic (start_time_id,start_time,end_time,passage_type,obj_type,number_plate) '
                        'VALUES (?,?,?,?,?,?)',
                        (start_time_id, start_time, end_time, passage_type, obj_type, number_plate),
                        False
                    )
                    info['criminal_img_name'] = None  # 因为没有违规所以没有违规图像名称
                    info['imgs'] = []
                elif info_type == 'illegal_parking':
                    excute_sql(
                        self.connection,
                        'INSERT INTO traffic (start_time_id,start_time,end_time,passage_type,obj_type,number_plate) '
                        'VALUES (?,?,?,?,?,?)',
                        (start_time_id, start_time, end_time, passage_type, obj_type, number_plate),
                        False
                    )
                    # 因为违规停车还是违规行为，需要记录到违规记录中
                    # 首先取出违规图像并保存
                    save_paths = []
                    for index, img in enumerate(info['imgs']):
                        img_name = start_time_id + ' ' + str(index) + '.jpg'
                        save_path = osp.join(self.img_save_path, img_name)
                        # 每次违规最少两张照片，取第二张存储在criminal_img_name
                        if index == 1:
                            info['criminal_img_name'] = img_name
                        save_path = save_path.replace(':', '-')  # opencv存储图片名字不能包括:
                        cv2.imwrite(save_path, img)
                        save_paths.append(save_path)
                    # 将保存的图像路径拼接起来存入数据库
                    img_path = reduce(lambda x, y: x + '_' + y, save_paths)
                    excute_sql(
                        self.connection,
                        'INSERT INTO criminal (start_time_id,number_plate,img_path,criminal_type) '
                        'VALUES (?,?,?,?)',
                        (start_time_id, number_plate, img_path, info_type),
                        False
                    )
                # 如果是违法占用车道信息
                elif info_type == 'illegal_occupation':
                    excute_sql(
                        self.connection,
                        'INSERT INTO traffic (start_time_id,start_time,end_time,passage_type,obj_type,number_plate) '
                        'VALUES (?,?,?,?,?,?)',
                        (start_time_id, start_time, end_time, passage_type, obj_type, number_plate),
                        False
                    )
                    # 因为非法占用车道还是违规行为，需要记录到违规记录中
                    # 首先取出违规图像并保存
                    save_paths = []
                    for index, img in enumerate(info['imgs']):
                        img_name = start_time_id + ' ' + str(index) + '.jpg'
                        save_path = osp.join(self.img_save_path, img_name)
                        # 每次违规最少两张照片，取第二张存储在criminal_img_name
                        if index == 1:
                            info['criminal_img_name'] = img_name
                        save_path = save_path.replace(':', '-')  # opencv存储图片名字不能包括:
                        cv2.imwrite(save_path, img)
                        save_paths.append(save_path)
                    # 将保存的图像路径拼接起来存入数据库
                    img_path = reduce(lambda x, y: x + '_' + y, save_paths)
                    excute_sql(
                        self.connection,
                        'INSERT INTO criminal (start_time_id,number_plate,img_path,criminal_type) '
                        'VALUES (?,?,?,?)',
                        (start_time_id, number_plate, img_path, info_type),
                        False
                    )
                continue
        return kwargs
