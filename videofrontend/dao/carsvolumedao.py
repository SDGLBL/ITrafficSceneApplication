import json
from datetime import datetime

import redis
from cfg import Cfg
from videofrontend.dao.mysqlpool import MysqlPool

from videofrontend.utils.utils import get_vehicle_violation_imag_path


class CarsVolumeDao(object):
    """
    有关车流量相关的数据库操作
    """

    def __init__(self):

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
        with MysqlPool() as db:
            db.cursor.execute("select passage_type, count(*)  as volume from traffic where  video_src=%s GROUP BY passage_type", (task_name))
            rows=db.cursor.fetchall()
            if len(rows)==0:
                line_chart_datas['isExist']=0
            else:
                for row in rows:
                    total += int(row["volume"])
                    for series in line_chart_datas["series"]:
                        if series["name"]==y_to_z[row["passage_type"]]:
                            series["data"].append(row["volume"])
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
                    db.cursor.execute("insert into tb_line_chart(left_num, right_num, straight_num, total_num, task_name) "
                                   "VALUES (%s,%s,%s,%s,%s)",(line_chart_datas["series"][0]["data"][-1],line_chart_datas["series"][1]["data"][-1],line_chart_datas["series"][2]["data"][-1],
                                                              line_chart_datas["series"][3]["data"][-1],task_name))
                    db.conn.commit()

                except:
                    db.conn.rollback()


    def set_task(self,task_name):
        """
        保存提交的任务
        :param task_name: 任务名
        :return:
        """
        try:
            snap_shot_path=get_vehicle_violation_imag_path(Cfg.snapshot_path,task_name)
            print(snap_shot_path)
            with MysqlPool() as db:
                db.cursor.execute("insert into tb_task_list(taskName,snapShotPath) VALUES (%s,%s) ",(task_name,snap_shot_path))
                db.conn.commit()

        except:
            db.conn.rollback()

    def get_task_list(self):
        """
        获取所有历史任务
        :return: 历史任务字典
        """
        tasks_list={'tasks':[],
                    "isExist":0}



        with MysqlPool() as db:
            db.cursor.execute("SELECT * FROM tb_task_list")
            datas=db.cursor.fetchall()

            for data in datas:
                task={'id':data["id"],
                      'date':datetime.strftime(data["commitDate"],"%Y-%m-%d %H:%M:%S"),
                      'task_name':data["taskName"],
                      'snapshot_path':data["snapShotPath"]}
                tasks_list['tasks'].append(task)
                tasks_list["isExist"]=1

        return tasks_list

    def get_history_traffic_volume_line_chart(self,task_name):
        """
        根据任务名查询违规历史折线图信息
        :param task_name: 任务名

        :return: 违规历史折线图信息
        """
        line_chart_datas = {
            "legend": {
                "data": ["左行驶车流量", "右行驶车流量", "前行驶车流量", "总车流量"]
            },
            "xAxis": {
                "data": []
            },
            "series": [
                {
                    "name": "左行驶车流量",
                    "data": []
                },
                {
                    "name": "右行驶车流量",
                    "data": []
                },
                {
                    "name": "前行驶车流量",
                    "data": []
                },
                {
                    "name": "总车流量",
                    "data": []
                }
            ],
            "isExist": 0
        }
        with MysqlPool() as db:
            db.cursor.execute("select record_time,left_num,right_num,straight_num,total_num from tb_line_chart "
                           "where task_name=%s" , (task_name))
            rows = db.cursor.fetchall()

            if len(rows)==0:
                line_chart_datas['isExist']=0
            else:
                for row in rows:
                    line_chart_datas["xAxis"]["data"].append(datetime.strftime(row["record_time"],"%Y-%m-%d %H:%M:%S"))
                    line_chart_datas["series"][0]["data"].append(row["left_num"])
                    line_chart_datas["series"][1]["data"].append(row["right_num"])
                    line_chart_datas["series"][2]["data"].append(row["straight_num"])
                    line_chart_datas["series"][3]["data"].append(row["total_num"])

                line_chart_datas['isExist']=1

        return line_chart_datas

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
