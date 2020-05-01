class BaseBuild(object):
    def __init__(self):
        """基础建造者类
        
        必须实现build和start方法,在build方法中应该根据需求组装好head detector backbones
        并根据性能需求决定component是否组合在一个进程中,或分发到多个进程中,也就是放在多个函
        数中.详细例子请自行看YoLov3TaskBuilder.

        Args:
            object ([type]): [description]
        """        
        super().__init__()

    def build(self):
        pass

    def start(self):
        """开始运行方法
        此方法必须使用多进程和进程队列,分别将build创建的函数使用多进程启动,编写过程请一定注意
        差错捕捉与处理,并在关键运行处添加Loger
        """        
        pass