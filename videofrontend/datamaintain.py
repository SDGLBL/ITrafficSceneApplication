from videofrontend.dao.carsvolumedao import CarsVolumeDao
from videofrontend.dao.vehicleviolationdao import VehicleViolationDao


class DataMaintenance(object):
    # 车流量Dao
    car_volume_dao = CarsVolumeDao()
    # 提交任务成功
    submit_task_success=False
    # 折线图历史数据
    line_chart_datas ={
            "legend":{
                "data":["左行驶车流量","右行驶车流量","前行驶车流量","总车流量"]
            },
            "xAxis":{
                "data":[]
            },
            "series":[
                {
                  "name":"左行驶车流量",
                  "data":[]
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
            "isExist":0
        }
    #启动任务所需要的一系列数据
    task_info={}
    vehicle_volume_dao=VehicleViolationDao()
    #场景编号，1，2，3，4
    scene_number= '-1'
    @staticmethod
    def init_data():
        """
        初始化数据
        :return:
        """
        DataMaintenance.car_volume_dao.reset_all_traffic_volume_statistics()
        DataMaintenance.line_chart_datas.clear()
        DataMaintenance.vehicle_volume_dao.rset_vehicle_violation_statistics()
        DataMaintenance.scene_number='-1'
        DataMaintenance.line_chart_datas ={
            "legend":{
                "data":["左行驶车流量","右行驶车流量","前行驶车流量","总车流量"]
            },
            "xAxis":{
                "data":[]
            },
            "series":[
                {
                  "name":"左行驶车流量",
                  "data":[]
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
            "isExist":0
        }
        DataMaintenance.task_info = {}
        DataMaintenance.submit_task_success = False


