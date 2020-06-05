import pymysql
from pymysql import cursors

from .logger import get_logger

logger = get_logger(filename='logs/database.log')


def get_connection(
        host: str,
        user: str,
        password: str,
        db: str,
        charset='utf8mb4',
        cursorclass=cursors.DictCursor):
    """获取数据库连接

    Arguments:
        host {str} -- mysql server host ip
        user {str} -- user name
        password {str} -- 连接密码
        db {str} -- 数据库名字

    Keyword Arguments:
        charset {str} -- 编码 (default: {'utf8mb4'})
        cursorclass {[type]} -- [description] (default: {cursors.DictCursor})

    Returns:
        Connection -- 数据库连接
    """    
    connection = pymysql.connect(
        host = host,
        user = user,
        password = password,
        db = db,
        charset = charset,
        cursorclass = cursorclass
    )
    return connection

def excute_sql(connection:pymysql.Connection,sql_str:str,args=(),is_return=False):
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



