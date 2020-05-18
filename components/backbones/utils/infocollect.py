from utils.dao import get_connection, excute_sql
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module
class InformationCollectorComponent(BaseBackboneComponent):
    """
    收集信息，存往数据库
    """

    def __init__(
            self,
            host: str,
            user: str,
            password: str,
            db: str,
            verbose=False,
            process_type=['pass']):
        super().__init__()
        self.connection = get_connection(host, user, password, db)
        self.process_type = process_type
        self.verbose = verbose

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
                object_id = int(info['id'])  # 目标id
                start_time = info['start_time']  # 被开始跟踪时间点
                end_time = info['end_time']  # 结束跟踪时间点
                passage_type = info['passage_type']  # 通行类型  直行 左转 右行
                obj_type = info['obj_type']  # 目标类型
                number_plate = info['number_plate']  # 车牌号 车牌号
                if passage_type == None:
                    passage_type = 'straight'
                # 处理通过信息
                if info_type == 'pass':
                    start_time_id = start_time + ' ' + str(object_id)
                    excute_sql(
                        self.connection,
                        'INSERT INTO traffic (start_time_id,start_time,end_time,passage_type,obj_type,number_plate) '
                        'VALUES (%s,%s,%s,%s,%s,%s)',
                        (start_time_id, start_time, end_time, passage_type, obj_type, number_plate),
                        False
                    )
                continue
        return kwargs
