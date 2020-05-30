import json
import os
import platform
import os.path as osp
from datetime import datetime

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
        if "analysis" in img_info.keys():
            for info in img_info['analysis']:
                if info['info_type'] != 'pass':
                    info.pop('start_time')
                    info.pop('passage_type')
                    info.pop('imgs')
                    info['criminal_img_path']=get_vehicle_violation_imag_path(Cfg.img_save_dir,info['criminal_img_name'])
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
            datas={'isExist':'0'}

        return datas

    def get_vehicle_violation_by_number_plate(self,number_plate):
        """
        根据车牌号查询查询违规信息
        :param number_plate:
        :param task_name:
        :return: 违规信息有且只有一条
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * from criminal where number_plate=%s",(number_plate))
        datas = cursor.fetchall()
        info={"criminal_img_path":[]}

        if len(datas)==0:
            info['isExist']='0'
            return info
        else:
            cursor.execute("SELECT c.criminal_type as info_type, c.start_time_id "
                           "as id, t.end_time,t.obj_type,c.number_plate,c.img_path "
                           "FROM criminal c inner join traffic t on c.number_plate = t.number_plate "
                           "where c.number_plate=%s",(number_plate))
            data=cursor.fetchone()
            info['info_type']=data[0]
            info['id']=data[1].split(" ")[2]
            info['end_time']=datetime.strftime(data[2],"%Y-%m-%d %H:%M:%S")
            info['obj_type']=data[3]
            info['number_plate']=data[4]
            for path in data[5].split("_"):
                info["criminal_img_path"].append(get_vehicle_violation_imag_path(Cfg.img_save_dir,path))
            info['isExist']='1'
            return info

    def rset_vehicle_violation_statistics(self):
        """
        重置车辆违规信息
        :return: Void
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




