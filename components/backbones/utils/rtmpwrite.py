import queue
import threading
import cv2
import subprocess as sp

from components.backbones.base import BaseBackboneComponent
from components.backbones.registry import BACKBONE_COMPONENT


@BACKBONE_COMPONENT.register_module

class RtmpWriteComponent(BaseBackboneComponent):
    def __init__(self,resolution,fps,rtmpUrl):
        super().__init__()
        # 自行设置 rtmp://localhost:1935/live/home
        self.command = ['ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', "{}x{}".format(resolution[0], resolution[1]),
                        '-r', str(fps),
                        '-i', '-',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'slow',
                        '-f', 'flv',
                        rtmpUrl]
        self.resolution=resolution
        self.p = sp.Popen(self.command, stdin=sp.PIPE)

    def read_frame(self,frame):
        self.frame_queue.put(frame)

    def process(self, **kwargs):
        super().process(**kwargs)
        imgs = kwargs['imgs']
        imgs_info = kwargs['imgs_info']
        for img,img_info in zip(imgs,imgs_info):
            if 'show_img' in img_info:
                img = img_info['show_img']
            if not (img.shape[1], img.shape[0]) == self.resolution:
                img = cv2.resize(img, self.resolution)
            self.p.stdin.write(img.tostring())
        return kwargs



