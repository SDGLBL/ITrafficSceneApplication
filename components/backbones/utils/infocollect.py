from time import time
from utils.dao import get_connection,excute_sql
from utils.logger import get_logger
from ..base import BaseBackboneComponent
from ..registry import BACKBONE_COMPONENT



class InformationCollectorComponent(BaseBackboneComponent):
    def __init__(
        self,
        host:str,
        user:str,
        password:str,
        db:str,):
        super().__init__()
        self.connection = get_connection(host,user,password,db)

    def process(self, **kwargs):
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img,imgs_info in zip(imgs,imgs_info):
            pass
        return kwargs