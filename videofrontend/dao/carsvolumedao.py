import pymysql
import redis

from cfg import Cfg
from task.configs.chenxiaotask import ChenXiaoTaskCfg



class CarsVolumeDao(object):
    """
    有关车流量相关的数据库操作
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

    """
    def get_traffic_volume_statistics(self):
        
        查询车流量信息
        :return: 查询结果
    
        cursor=self.connection.cursor()
        cursor.execute("select passage_type, count(*) from traffic GROUP BY passage_type")
        datas = {'total_cars':0,'straight':0,'left':0,'right':0}
        total_cars=0
        rows=cursor.fetchall()
        for row in rows:
            print(row)
            datas[row[0]]=row[1]
            total_cars += int(row[1])

        datas['total_cars']=total_cars
        return datas
    """

    def set_traffic_volume_statistics(self, img_info):
        """
        存入车流量相关数据
        :return:
        """

        self.redis.set('pass_count',img_info['pass_count'])
        self.redis.set('left_pass_count',img_info['left_pass_count'])
        self.redis.set('right_pass_count', img_info['right_pass_count'])
        self.redis.set('straight_pass_count', img_info['straight_pass_count'])
        self.redis.set('car_pass_count', img_info['car_pass_count'])
        self.redis.set('truck_pass_count', img_info['truck_pass_count'])
        self.redis.set('bus_pass_count', img_info['bus_pass_count'])

    def get_traffic_volume_statistics(self):
        """
        实时获取当前车流量数据
        :return: 车流量数据
        """
        datas = {'pass_count': self.redis.get('pass_count'),
                 'left_pass_count': self.redis.get('left_pass_count'),
                 'right_pass_count': self.redis.get('right_pass_count'),
                 'straight_pass_count': self.redis.get('straight_pass_count'),
                 'car_pass_count': self.redis.get('car_pass_count'),
                 'truck_pass_count': self.redis.get('truck_pass_count'),
                 'bus_pass_count': self.redis.get('bus_pass_count')}
        return datas

    def reset_all_traffic_volume_statistics(self):
        """
        重置车流量数据
        :return:
        """
        self.redis.set('pass_count', 0)
        self.redis.set('left_pass_count', 0)
        self.redis.set('right_pass_count', 0)
        self.redis.set('straight_pass_count', 0)
        self.redis.set('car_pass_count', 0)
        self.redis.set('truck_pass_count', 0)
        self.redis.set('bus_pass_count', 0)


if __name__ == '__main__':
    img_info = {'pass_count': '100',
                'left_pass_count':'25',
                'right_pass_count': '26',
                'straight_pass_count': '30',
                'car_pass_count': '5',
                'truck_pass_count': '8',
                'bus_pass_count': '23'}

    car_volume_dao=CarsVolumeDao()

    car_volume_dao.set_traffic_volume_statistics(img_info)

    datas=car_volume_dao.get_traffic_volume_statistics()


    print(datas)
