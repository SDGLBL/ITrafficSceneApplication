from llist import dllist, dllistnode
from utils.logger import get_logger

class ImgInfoPool(object):
    def __init__(self,max_size = 60):
        super().__init__()
        self.task_analysis_info = {}
        self.task_pass_count_table = {}
        self.task_progress = {}
        self.max_size = max_size
        self.logger = get_logger()


    def add(self,task_name: str,img_info: dict):
        if task_name not in self.task_analysis_info.keys():
            # 初始化分析信息保存链表
            self.task_analysis_info[task_name] = dllist()
            # 初始化task运行进度为0
            self.task_progress[task_name] = 0
            # 初始化task通行记录表
            if 'pass_count_table' in img_info.keys():
                self.task_pass_count_table[task_name] = img_info['pass_count_table'][0]
        # 刷新task进度
        if 'video_len' in img_info.keys():
            self.task_progress[task_name] = '{:.2f}'.format(img_info['index'] / img_info['video_len'] * 100)
        # 预处理分析信息
        if 'analysis' in img_info.keys():
            analysis_info = img_info['analysis']
            if len(analysis_info) > 0:
                if len(self.task_analysis_info[task_name]) >= self.max_size:
                    # 弹出分析信息保存链表最旧的信息
                    self.task_analysis_info[task_name].popleft()
                    # 在v后插入最新的信息
                    self.task_analysis_info[task_name].append(analysis_info)
                else:
                    # 在分析信息保存链表后插入最新的信息
                    self.task_analysis_info[task_name].append(analysis_info)
        # 刷新通行记录表格
        # 如果表格刷新了
        if 'pass_count_table' in img_info.keys():
            is_table_refresh = img_info['pass_count_table'][1]
            if is_table_refresh:
                self.task_pass_count_table[task_name] = img_info['pass_count_table'][0]

    
    def get_progress_info(self,task_name: str):
        if task_name not in self.task_progress.keys():
            raise RuntimeError('Task信息池中不存在task_name为{}的进度信息'.format(task_name))
        return self.task_progress[task_name]

    def get_analysis_info(self,task_name: str):
        if not self.exist(task_name):
            raise RuntimeError('Task信息池中不存在task_name为{}的task_analysis_info信息队列'.format(task_name))
        if len(self.task_analysis_info[task_name]) == 0:
            raise RuntimeError('Task信息池中task_name为{}的task_analysis_info信息队列已空')
        return self.task_analysis_info[task_name].pop()
    
    def get_pass_count_table(self,task_name: str):
        if task_name not in self.task_pass_count_table.keys():
            raise RuntimeError('Task信息池中不存在task_name为{}的通行表格信息'.format(task_name))
        return self.task_pass_count_table[task_name]

    def remove(self,task_name: str):
        if not self.exist(task_name):
            raise RuntimeError('Task信息池中不存在task_name为{}的task_analysis_info信息队列'.format(task_name))
        self.logger.info('清空信息池中{} task的输出信息'.format(task_name))
        del self.task_analysis_info[task_name]
        del self.task_pass_count_table[task_name]
        del self.task_progress[task_name]
    
    def exist(self,task_name: str):
        if task_name not in self.task_analysis_info.keys():
            return False
        return True


