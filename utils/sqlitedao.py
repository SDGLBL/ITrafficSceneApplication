import sqlite3
import os
from .logger import get_logger
from cfg import DataConfig



def get_connection(
        data_base:str
        ):
    """获取数据库连接
    """
    connection = sqlite3.connect(data_base)
    return connection

def excute_sql(connection:sqlite3.Connection,sql_str:str,args=(),is_return=False):
    """执行sql语句

    Arguments:
        connection {pymysql.Connection} -- mysql connection
        sql_str {str} -- 执行的语句

    Keyword Arguments:
        args {tuple} -- 执行的语句需要的参数
        is_return {bool} -- 当前执行的语句是否会返回值 (default: {False})

    Raises:
        AttributeError: args必须要为元组

    Returns:
        [type] -- [description]
    """
    if not isinstance(args,tuple):
        raise AttributeError('args必须为元组')
    cursor = connection.cursor()
    if len(args) != 0:
        cursor.execute(sql_str, args)
    else:
        cursor.execute(sql_str) 
    if is_return:
        result = cursor.fetchall()
        return result
    else:
        connection.commit()
        cursor.close()
    return None

def create_database(clear_exist = False):
    """创建项目存储数据需要使用的数据库

    Args:
        clear_exist (bool, optional): 是否先清除已经存在的db数据库. Defaults to False.
    """
    if os.path.exists(DataConfig.DATABASE_PATH) and clear_exist:
        # 清理违规图像
        os.remove(DataConfig.DATABASE_PATH)
        for name in os.listdir(DataConfig.CRIMINAL_DIR):
            if name == 'upload':
                continue
            os.remove(os.path.join(DataConfig.CRIMINAL_DIR,name))
    create_traffic_str = "CREATE TABLE IF NOT EXISTS traffic (start_time_id TEXT NOT NULL,start_time INTEGER NOT NULL,end_time INTEGER NOT NULL,passage_type TEXT DEFAULT straight,obj_type TEXT DEFAULT car,number_plate TEXT,other_info TEXT,CONSTRAINT traffic_PK PRIMARY KEY (start_time_id));"
    create_criminal_str = "CREATE TABLE IF NOT EXISTS criminal (start_time_id TEXT NOT NULL,number_plate TEXT,img_path TEXT,criminal_type TEXT NOT NULL,CONSTRAINT criminal_PK PRIMARY KEY (start_time_id),CONSTRAINT criminal_FK FOREIGN KEY (start_time_id) REFERENCES traffic(start_time_id));"
    conn = get_connection(DataConfig.DATABASE_PATH)
    excute_sql(conn,create_traffic_str)
    excute_sql(conn,create_criminal_str)