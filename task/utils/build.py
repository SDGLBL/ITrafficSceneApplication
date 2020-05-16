from queue import Empty, Full

import torch
from torch.multiprocessing import Process, Queue

from components.backbones.registry import BACKBONE_COMPONENT
from components.detector.registry import DETECTOR
from components.head.registry import HEAD
from components.tracker.registry import TRACKER
from utils.logger import get_logger
from utils.registry import build_from_cfg

logger = get_logger()

def __build_head_component(head_component_cfg):
    return build_from_cfg(head_component_cfg, HEAD)


def __build_detector_component(detector_component_cfg):
    return build_from_cfg(detector_component_cfg, DETECTOR)


def __build_tracker_component(tracker_component_cfg):
    return build_from_cfg(tracker_component_cfg, TRACKER)


def __build_backbone_component(backbone_component_cfg):
    return build_from_cfg(backbone_component_cfg, BACKBONE_COMPONENT)


# 定义head 进程的运行函数
def __head_process(head_cfg, sendqs, timeout):
    head = __build_head_component(head_cfg)
    logger.info('create ' + str(head_cfg) + ' and which len is {}'.format(len(head)))
    try:
        for kwargs in head:
            for sendq in sendqs:
                sendq.put(kwargs, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the head process')
    except Full:
        logger.info('head管道长时间爆满，可能detector出现了问题')
    except Exception as e:
        logger.exception(e)
    finally:
        for sendq in sendqs:
            sendq.close()
        logger.info('release the head source')


# 定义detector 进程的运行函数
def __detector_process(detector_cfg, recivq: Queue, sendqs, timeout):
    detector = __build_detector_component(detector_cfg)
    logger.info('create ' + str(detector_cfg))
    try:
        while True:
            kwargs = recivq.get(timeout=timeout)
            kwargs = detector(**kwargs)
            # 因为后续可能是backbones也可能是tracker所以使用list来发送
            for sendq in sendqs:
                sendq.put(kwargs, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the detector process')
    except Empty:
        logger.info('head不再发送数据detector自动释放')
    except Exception as e:
        logger.exception(e)
    finally:
        del detector  # 清除探测器对象
        torch.cuda.empty_cache()  # 清空GPU缓存，防止出现进程STOP占用显存
        for sendq in sendqs:
            sendq.close()
        logger.info('release the detector source')


def __tracker_process(tracker_cfg, recivq: Queue, sendqs, timeout):
    tracker = __build_tracker_component(tracker_cfg)
    logger.info('create ' + str(tracker_cfg))
    try:
        while True:
            kwargs = recivq.get(timeout=timeout)
            imgs, imgs_info = kwargs['imgs'], kwargs['imgs_info']
            for index, (img, img_info) in enumerate(zip(imgs, imgs_info)):
                img_info = tracker(img, img_info)
                imgs_info[index] = img_info
            for sendq in sendqs:
                sendq.put({'imgs': imgs, 'imgs_info': imgs_info}, timeout=timeout)
    except KeyboardInterrupt:
        logger.info('user stop the detector process')
    except Empty:
        logger.info('detector不再发送数据tracker自动释放')
    except Exception as e:
        logger.exception(e)
    finally:
        del tracker  # 清除探测器对象
        torch.cuda.empty_cache()  # 清空GPU缓存，防止出现进程STOP占用显存
        for sendq in sendqs:
            sendq.close()
        logger.info('release the tracker source')


def __backbone_process(backbone_cfg: list, recivq: Queue, timeout):
    # 实例化一个backbone里面所有的组件
    backbone_components = [__build_backbone_component(bbcfg) for bbcfg in backbone_cfg]
    logger.info('create backbone {0} '.format(backbone_cfg))
    try:
        while True:
            kwargs = recivq.get(timeout=timeout)
            # 首先由该管道内的第一个组件处理数据
            kwargs = backbone_components[0](**kwargs)
            if len(backbone_components) > 1:
                # 如果该管道有多个component的话依次将数据交给之后的component处理
                for backbone_component in backbone_components[1:]:
                    kwargs = backbone_component(**kwargs)
                # 处理到最后的数据直接清楚
            del kwargs
    except KeyboardInterrupt:
        logger.info('user stop a backbone_process process')
    except Empty:
        logger.info('backbone normal stoped')
    except Exception as e:
        logger.exception(e)
    return


def build_process(cfg_type, cfg, recivqs, sendqs, timeout):
    if cfg_type == 'head':
        return [Process(target=__head_process, args=(cfg[0], sendqs, timeout,))]
    elif cfg_type == 'detector':
        return [Process(target=__detector_process, args=(cfg[0], recivqs[0], sendqs, timeout,))]
    elif cfg_type == 'tracker':
        return [Process(target=__tracker_process, args=(cfg[0], recivqs[0], sendqs, timeout,))]
    elif cfg_type == 'backbones':
        return [Process(target=__backbone_process, args=(backbone_cfg, recivq, timeout)) for backbone_cfg, recivq in
                zip(cfg, recivqs)]
    else:
        raise AttributeError('暂时不支持类型为{}的组件'.format(cfg_type))
