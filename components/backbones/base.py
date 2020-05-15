
class BaseBackboneComponent(object):
    def __init__(self):
        pass

    def process(self, **kwargs):
        """
        处理函数，处理来自head的数据
        """
        pass

    def __call__(self, *args, **kwargs):
        return self.process(**kwargs)
