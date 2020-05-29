import json
from datetime import datetime

import pymysql
import redis

from cfg import Cfg



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

    def get_traffic_volume_line_chart_statistics(self,task_name,line_chart_datas):
        """
        通过制定任务名,时间粒度划分来获取车流量折线图统计数据
        :param line_chart_datas: 折线图数据字典
        :param task_name:任务名
        :return:
        """

        #英转中字典
        y_to_z={
                "left":"左行驶车流量",
                "right":"右行驶车流量",
                "straight":"前行驶车流量"
        }
        #存在字典查看是否有添加数据进入line_chart_datas
        isExist=[]

        total = 0
        cursor = self.connection.cursor()
        cursor.execute("select passage_type, count(*) as volume from traffic where  video_src=%s GROUP BY passage_type", (task_name))
        rows=cursor.fetchall()
        if len(rows)==0:
            line_chart_datas['isExist']=0
        else:
            for row in rows:
                total += int(row[1])
                for series in line_chart_datas["series"]:
                    if series["name"]==y_to_z[row[0]]:
                        series["data"].append(row[1])
                        isExist.append(series["name"])
                        break
            line_chart_datas['isExist']=1
            for series in line_chart_datas["series"]:
                if series["name"] == "总车流量":
                    series["data"].append(total)
                    isExist.append(series["name"])
                if series["name"] not in isExist:
                    series["data"].append(0)
            line_chart_datas["xAxis"]["data"].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        if line_chart_datas['isExist']==1:
            try:
                cursor.execute("insert into tb_line_chart(left_num, right_num, straight_num, total_num, task_name) "
                               "VALUES (%s,%s,%s,%s,%s)",(line_chart_datas["series"][0]["data"][-1],line_chart_datas["series"][1]["data"][-1],line_chart_datas["series"][2]["data"][-1],
                                                          line_chart_datas["series"][3]["data"][-1],task_name))
                self.connection.commit()

            except:
                self.connection.rollback()


        return line_chart_datas

    def set_task(self,task_name):
        """
        保存提交的任务
        :param task_name: 任务名
        :return:
        """
        cursor=self.connection.cursor()
        try:
            cursor.execute("insert into tb_task_list(taskName) VALUES (%s)",(task_name))
            self.connection.commit()

        except:
            self.connection.rollback()

    def get_task_list(self):
        """
        获取所有历史任务
        :return: 历史任务字典
        """
        tasks_list={'tasks':[]}

        cursor=self.connection.cursor()
        cursor.execute("SELECT * FROM tb_task_list")
        datas=cursor.fetchall()
        for data in datas:
            task={'date':datetime.strftime(data[1],"%Y-%m-%d %H:%M:%S"),
                  'task_name':data[2]}
            tasks_list['tasks'].append(task)

        return tasks_list

    def get_history_traffic_volume_line_chart(self,task_name,start_time,end_time):
        """
        根据车牌号，起始时间，结束时间，时间粒度。查询违规历史折线图信息
        :param task_name: 任务名
        :param start_time: 起始时间
        :param end_time: 结束时间
        :return: 时间间隔内的违规历史折线图信息
        """
        cursor=self.connection.cursor()
        cursor.execute("select record_time,left_num,right_num,straight_num,total_num from tb_line_chart "
                       "where task_name=%s and record_time between %s and %s" , (task_name,start_time,end_time))
        rows = cursor.fetchall()
        datas={'line_datas':[]}
        if len(rows)==0:
            datas['isExist']=0
        else:
            for row in rows:
                data = {'pass_count': row[4],
                        'left_pass_count': row[1],
                        'right_pass_count': row[2],
                        'straight_pass_count': row[3],
                        'time_now': datetime.strftime(row[0],"%Y-%m-%d %H:%M:%S") }
                datas['line_datas'].append(data)
            datas['isExist']=1

        return datas

    def set_pass_count_table_statistics(self,img_info):
        """
        存入车流量表数据
        :param pass_count_table: 车流量表数据
        :return: void
        """
        datas={}
        if "pass_count_table" in img_info.keys():
            datas['pass_count_table']=img_info['pass_count_table']
            datas['isExist']=1
        else:
            datas['isExist']=0
        self.redis.set('pass_count_table',json.dumps(datas))

    def get_pass_count_table_statistics(self):
        """
        获取车流量表数据
        :param pass_count_table:
        :return: 车流量表数据
        """
        datas=json.loads(self.redis.get('pass_count_table'))
        if datas:
            return datas
        else:
            datas={}
            datas['isExist']=0
            return datas

    def set_real_time_vehicle_statistics(self,img_info):
        """
        存入实时车辆信息(pass)
        :return: 实时车辆信息列表
        """
        datas = {'analysis': []}
        for info in img_info['analysis']:
            if info['info_type'] == 'pass':
                info.pop('info_type')
                info.pop('id')
                info.pop('start_time')
                info.pop('imgs')
                info.pop('criminal_img_path')
                datas['analysis'].append(info)

        if len(datas['analysis']) == 0:
            datas['exist'] = 0
        else:
            datas['exist'] = 1
        self.redis.set('vehicle_info', json.dumps(datas))

    def get_real_time_vehicle_statistics(self):
        """
        获取实时车辆信息(pass)
        :return: 实时车辆信息列表
        """

        data = self.redis.get('vehicle_info')
        if data:
            datas = json.loads(data)
        else:
            datas = {'isexist': '0'}

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
        self.redis.delete('pass_count_table')
        self.redis.delete('vehicle_info')


if __name__=='__main__':
    pass_count_table = [
        [' ', '左拐', '右拐', '直行', '总计'],
        ['巴士', 0, 0, 1, 1],
        ['小汽车', 1, 0, 1, 2],
        ['卡车', 1, 1, 0, 2],
        ['总计', 2, 1, 2, 5]
    ]

    img_info = {
        "analysis": [
            {"info_type": 'pass',
             "id": "14.0",
             "start_time": "2020-05-10 15:04:17",
             "end_time": "2020-05-20 15:04:17",
             "passage_type": None,
             "obj_type": "car",
             "number_plate": "浙K8F019",
             "criminal_img_path": "2020-05-18 14-37-47 23 1.jpg",
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
                "criminal_img_path": "2020-05-18 14-41-58 170 1.jpg",
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
                "criminal_img_path": "2020-05-18 14-41-58 170 1.jpg",
                "imgs": "asd"
            }
        ]
    }

    car=CarsVolumeDao()

    datas=car.get_traffic_volume_line_chart_statistics("lot_15.mp4")
    print(datas)
