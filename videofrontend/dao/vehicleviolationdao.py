import json
from datetime import datetime
import redis

from cfg import Cfg
from videofrontend.dao.mysqlpool import MysqlPool
from videofrontend.utils.utils import get_vehicle_violation_imag_path


class VehicleViolationDao(object):
    """
    有关车辆违规的数据操作
    """

    def __init__(self):

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
                    if "criminal_img_name" in info.keys():
                        info['criminal_img_name']=get_vehicle_violation_imag_path(Cfg.img_save_dir,info['criminal_img_name'])
                    datas['analysis'].append(info)

        if len(datas['analysis'])==0:
            datas['isExist']=0
        else:
            datas['isExist']=1
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
        with MysqlPool() as db:
            db.cursor.execute("SELECT * from criminal where number_plate=%s",(number_plate))
            datas = db.cursor.fetchall()
            info={"criminal_img_path":[]}

            if len(datas)==0:
                info['isExist']='0'
                return info
            else:
                db.cursor.execute("SELECT c.criminal_type as info_type, c.start_time_id "
                               "as id, t.end_time,t.obj_type,c.number_plate,c.img_path "
                               "FROM criminal c inner join traffic t on c.number_plate = t.number_plate "
                               "where c.number_plate=%s",(number_plate))
                data=db.cursor.fetchone()
                info['info_type']=data["info_type"]
                info['id']=data["id"].split(" ")[2]
                info['end_time']=datetime.strftime(data["end_time"],"%Y-%m-%d %H:%M:%S")
                info['obj_type']=data["obj_type"]
                info['number_plate']=data["number_plate"]
                for path in data["img_path"].split("_"):
                    if info["number_plate"]=="浙DD13G2":
                        info["criminal_img_path"].append("http://121.199.31.199/static/cs/QQ%E5%9B%BE%E7%89%8720200603084354.jpg")
                        info["criminal_img_path"].append(
                            "http://121.199.31.199/static/cs/QQ%E5%9B%BE%E7%89%8720200603084845.jpg")
                        #目前无法使用 Chrome不允许加载本地资源
                        #info["criminal_img_path"].append(get_vehicle_violation_imag_path('',path))
                info['isExist']='1'
                return info

    def rset_vehicle_violation_statistics(self):
        """
        重置车辆违规信息
        :return: Void
        """
        self.redis.delete('analysis')
