import json
import os
import platform
import os.path as osp
import cv2 as cv
import pymysql
import redis

from cfg import Cfg
from videofrontend.utils.utils import get_vehicle_violation_imag_path


class VehicleViolationDao(object):
    """
    有关车辆违规的数据操作
    """

    def __init__(self):
        self.connection = pymysql.connect(host=Cfg.host,
                                          port=Cfg.port,
                                          user=Cfg.user,
                                          password=Cfg.password,
                                          db=Cfg.database,
                                          charset=Cfg.charset)
        self.redis = redis.StrictRedis(host=Cfg.redis_host, port=Cfg.redis_port,
                                       decode_responses=Cfg.redis_decode_responses,db=Cfg.redis_database)

    def set_vehicle_violation_statistics(self,img_info):
        """
        将img_info中的车辆违规信息存入redis中
        :return:
        """
        datas={'analysis':[]}
        for info in img_info['analysis']:
            if info['info_type'] != 'pass':
                info.pop('start_time')
                info.pop('passage_type')
                info.pop('imgs')
                info['criminal_img_name']=get_vehicle_violation_imag_path(info['criminal_img_name'])
                datas['analysis'].append(info)

        if len(datas['analysis'])==0:
            datas['exist']=0
        else:
            datas['exist']=1
        self.redis.set('analysis',json.dumps(datas))

    def get_vehicle_violation_statistics(self):
        """
        将analysis从redis取出并发送到views
        0表示没有违规的车辆信息,1表示右违规的车辆信息
        :return: analysis数据

        """

        data=self.redis.get('analysis')
        if data:
            datas = json.loads(data)
        else:
            datas={'isexist':'0'}

        return datas

    def rset_vehicle_violation_statistics(self):
        """
        重置车辆违规信息
        :return:
        """
        self.redis.delete('analysis')


if __name__ == '__main__':
    img_info={
    "analysis": [
        {"info_type":'pass',
         "id": "14.0",
         "start_time": "2020-05-10 15:04:17",
         "end_time": "2020-05-20 15:04:17",
         "passage_type":None,
         "obj_type": "car",
         "number_plate": "浙K8F019",
         "criminal_img_name":"2020-05-18 14-37-47 23 1.jpg",
         "imgs": "asd"
         },
        {
            "info_type": "illegal_parking",
            "id": "32.0",
            "start_time": "2020-05-10 15:04:17",
            "end_time": "2020-05-20 15:04:17",
            "passage_type": None,
            "obj_type": "trunk",
            "number_plate": "浙K8F019",
            "criminal_img_name": "2020-05-18 14-41-58 170 1.jpg",
            "imgs": "asd"
        },
        {
            "info_type": "illegal_parking",
            "id": "62.0",
            "start_time": "2020-05-10 15:04:17",
            "end_time": "2020-05-21 15:04:17",
            "passage_type": None,
            "obj_type": "car",
            "number_plate": "浙K8F029",
            "criminal_img_name": "2020-05-18 14-41-58 170 1.jpg",
            "imgs":"asd"
        }
    ]
}




