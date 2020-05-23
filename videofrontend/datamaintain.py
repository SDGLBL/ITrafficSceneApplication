from multiprocessing import Pipe
import redis

from videofrontend.dao.carsvolumedao import CarsVolumeDao


class DataMaintenance(object):
    # 车流量Dao
    car_volume_dao=CarsVolumeDao()

