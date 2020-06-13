from llist import dllist, dllistnode
from utils.logger import get_logger

class ImgInfoPool(object):
    def __init__(self,max_size = 60):
        super().__init__()
        self.task_img_info = {}
        self.max_size = max_size
        self.logger = get_logger('logs/infoPool.log')


    def add(self,task_name: str,img_info: dict):
        if task_name not in self.task_img_info.keys():
            self.task_img_info[task_name] = dllist()
        if len(self.task_img_info[task_name]) >= self.max_size:
            # 弹出链表最旧的信息
            self.task_img_info[task_name].popleft()
            # 在链表后插入最新的信息
            self.task_img_info[task_name].append(img_info)
        else:
            # 在链表后插入最新的信息
            self.task_img_info[task_name].append(img_info)

    def get(self,task_name: str):
        if task_name not in self.task_img_info.keys():
            raise RuntimeError('Task信息池中不存在task_name为{}的Img_info信息队列'.format(task_name))
        try:
            img_info = self.task_img_info[task_name].pop()
            return img_info
        except ValueError:
            return None


    def remove(self,task_name: str):
        if task_name not in self.task_img_info.keys():
            raise RuntimeError('Task信息池中不存在task_name为{}的Img_info信息队列'.format(task_name))
        self.logger.info('清空信息池中{} task的输出信息')
        del self.task_img_info[task_name]


