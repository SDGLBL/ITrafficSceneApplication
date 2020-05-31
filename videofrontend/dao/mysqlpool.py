import pymysql

from DBUtils.PooledDB import PooledDB

from cfg import Cfg


class MysqlPool:
    config = {
        'creator': pymysql,
        'host': Cfg.host,
        'port': Cfg.port,
        'user': Cfg.user,
        'password': Cfg.password,
        'db': Cfg.database,
        'charset': Cfg.charset,
        'maxconnections': 70,  # 连接池最大连接数量
        'cursorclass': pymysql.cursors.DictCursor
    }
    pool = PooledDB(**config)

    def __enter__(self):
        self.conn = MysqlPool.pool.connection()
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.conn.close()