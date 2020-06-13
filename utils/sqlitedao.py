import sqlite3
from .logger import get_logger

logger = get_logger(filename='logs/database.log')


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
    try:
        with connection.cursor() as cursor:
            if len(args) != 0:
                cursor.execute(sql_str, args)
            else:
                cursor.execute(sql_str)
        if is_return:
            result = cursor.fetchone()
            return result
        else:
            connection.commit()
    except Exception as e:
        logger.exception(e)
    return None