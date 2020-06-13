from .manage import TaskManager,ImgInfoPool

def get_cfgDataHandler():
    from .manage import TaskCfgDataHandler
    return TaskCfgDataHandler()